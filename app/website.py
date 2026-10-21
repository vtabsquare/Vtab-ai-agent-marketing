"""Bounded website intelligence for standalone and hybrid workspaces."""
import gc
import hashlib
import ipaddress
import re
import time
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import httpx
from .tools import CheckFailure, memory_trim

INJECTION_PATTERNS = (
    r'ignore\s+(all|previous)\s+instructions',
    r'system\s+prompt',
    r'developer\s+message',
    r'exfiltrat',
    r'reveal\s+.*secret',
)


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ''
        self.description = ''
        self.text = []
        self.links = []
        self._in_title = False
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag in {'script', 'style', 'noscript', 'svg'}:
            self._skip += 1
        if tag == 'title':
            self._in_title = True
        if tag == 'meta' and data.get('name', '').lower() in {'description', 'og:description'}:
            self.description = data.get('content', '')
        if tag == 'a' and data.get('href'):
            self.links.append(data['href'])

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'noscript', 'svg'} and self._skip:
            self._skip -= 1
        if tag == 'title':
            self._in_title = False

    def handle_data(self, data):
        value = ' '.join(unescape(data).split())
        if not value or self._skip:
            return
        if self._in_title:
            self.title = (self.title + ' ' + value).strip()
        self.text.append(value)


def is_same_site(host1: str, host2: str) -> bool:
    """Return True if host1 and host2 are the same site (e.g. example.com and www.example.com or subdomains)."""
    h1 = (host1 or '').lower().split(':')[0]
    h2 = (host2 or '').lower().split(':')[0]
    if h1 == h2:
        return True
    s1 = h1[4:] if h1.startswith('www.') else h1
    s2 = h2[4:] if h2.startswith('www.') else h2
    if s1 == s2:
        return True
    return s1.endswith('.' + s2) or s2.endswith('.' + s1)


def validate_public_url(url: str):
    url_clean = (url or '').strip()
    if not re.match(r'^https?://', url_clean, re.I):
        url_clean = 'https://' + url_clean
    parsed = urlparse(url_clean)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password:
        raise CheckFailure('Enter a public HTTP or HTTPS website URL.')
    host = parsed.hostname.lower()
    if host in {'localhost', 'localhost.localdomain'} or host.endswith('.local'):
        raise CheckFailure('Private or local website addresses are not allowed.')
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise CheckFailure('Private or reserved website addresses are not allowed.')
    return parsed


class WebsiteIntelligence:
    def __init__(self, store):
        self.store = store

    def _get(self, url, max_redirects=3):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (compatible; MarketingOS/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        curr_url = url
        for _ in range(max_redirects + 1):
            parsed = validate_public_url(curr_url)
            try:
                response = httpx.get(
                    curr_url,
                    headers=headers,
                    timeout=12,
                    follow_redirects=False,
                )
            except Exception as exc:
                raise CheckFailure(f'Could not reach {curr_url}: {str(exc)}') from None

            if 300 <= response.status_code < 400:
                location = response.headers.get('location')
                if not location:
                    raise CheckFailure('Website returned an invalid redirect.')
                target = urljoin(curr_url, location)
                redirected = validate_public_url(target)
                if not is_same_site(parsed.hostname, redirected.hostname):
                    raise CheckFailure(f'Cross-domain redirects from {parsed.hostname} to {redirected.hostname} are not followed.')
                curr_url = target
                continue

            response.raise_for_status()
            if len(response.content) > 2_000_000:
                raise CheckFailure('Website page is too large to ingest safely.')
            return response, curr_url

        raise CheckFailure('Too many redirects encountered while scanning website.')

    def scan(self, root_url, max_pages=5):
        if not root_url or not root_url.strip():
            raise CheckFailure('Please enter a website URL.')

        # Resolve initial canonical root (handles http->https and apex->www redirects)
        root_parsed = validate_public_url(root_url)
        clean_root = f'{root_parsed.scheme}://{root_parsed.netloc}{root_parsed.path or ""}'.rstrip('/')
        if not clean_root:
            clean_root = f'{root_parsed.scheme}://{root_parsed.netloc}'

        response, canonical_url = self._get(clean_root)
        canon_parsed = validate_public_url(canonical_url)
        base = f'{canon_parsed.scheme}://{canon_parsed.netloc}'
        urls = [canonical_url.rstrip('/') or base]

        # Attempt to discover sitemap URLs safely
        try:
            sitemap_resp, _ = self._get(urljoin(base, '/sitemap.xml'))
            if 'xml' in sitemap_resp.headers.get('content-type', '') or sitemap_resp.text.lstrip().startswith('<?xml'):
                tree = ElementTree.fromstring(sitemap_resp.content)
                for element in tree.iter():
                    if element.tag.endswith('loc') and element.text:
                        candidate = element.text.strip()
                        c_parsed = validate_public_url(candidate)
                        if is_same_site(c_parsed.hostname, canon_parsed.hostname):
                            norm_candidate = candidate.rstrip('/')
                            if norm_candidate not in urls:
                                urls.append(norm_candidate)
        except Exception:
            pass

        # Also extract internal links from root page HTML if sitemap gave few links
        if len(urls) <= 1:
            try:
                root_parser = _PageParser()
                root_parser.feed(response.text[:200_000])
                for href in root_parser.links:
                    joined = urljoin(canonical_url, href)
                    try:
                        p = validate_public_url(joined)
                        if is_same_site(p.hostname, canon_parsed.hostname):
                            norm_link = joined.split('#')[0].split('?')[0].rstrip('/')
                            if norm_link and norm_link not in urls:
                                urls.append(norm_link)
                    except Exception:
                        pass
            except Exception:
                pass

        pages = []
        candidate_items = []
        target_limit = max(1, min(max_pages or 5, 8))

        for u in urls[:target_limit]:
            try:
                r, final_u = self._get(u) if u != canonical_url else (response, canonical_url)
                if 'text/html' not in r.headers.get('content-type', 'text/html'):
                    continue
                parser = _PageParser()
                parser.feed(r.text[:500_000])
                text = ' '.join(parser.text)[:12000]
                suspicious = any(re.search(pat, text, re.I) for pat in INJECTION_PATTERNS)
                digest = hashlib.sha256((final_u + '\n' + text).encode()).hexdigest()
                page = {
                    'url': final_u,
                    'title': parser.title[:500] or final_u,
                    'description': parser.description[:1200],
                    'content_hash': digest,
                    'retrieved_at': time.time(),
                    'suspicious': suspicious,
                    'text_excerpt': text[:2500],
                }
                pages.append(page)
                summary = parser.description or ' '.join(parser.text[:8])
                if summary:
                    candidate_items.append({
                        'kind': 'website_summary',
                        'key': final_u,
                        'value': summary[:2500],
                        'source_url': final_u,
                        'evidence': text[:1200],
                        'confidence': 0.75 if not suspicious else 0.2,
                        'sensitivity': 'public',
                        'status': 'discovered',
                        'content_hash': digest,
                    })
                for match in re.finditer(r'(?i)(?:₹|INR|USD|EUR|GBP|\$|€|£)\s?[0-9][0-9,.]*(?:\s?(?:per|/)[a-z]+)?', text):
                    candidate_items.append({
                        'kind': 'price_candidate',
                        'key': final_u + '#price-' + str(match.start()),
                        'value': match.group(0)[:120],
                        'source_url': final_u,
                        'evidence': text[max(0, match.start() - 100):match.end() + 100],
                        'confidence': 0.65,
                        'sensitivity': 'public',
                        'status': 'discovered',
                        'content_hash': digest,
                    })
            except Exception:
                continue

        try:
            return self.store.save_website_scan(root_url, pages, candidate_items)
        finally:
            memory_trim()
