"""Bounded website intelligence for standalone and hybrid workspaces."""
import hashlib
import ipaddress
import re
import time
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import httpx
from .tools import CheckFailure

INJECTION_PATTERNS=(r'ignore\s+(all|previous)\s+instructions',r'system\s+prompt',r'developer\s+message',r'exfiltrat',r'reveal\s+.*secret')

class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.title=''; self.description=''; self.text=[]; self.links=[]; self._in_title=False; self._skip=0
    def handle_starttag(self,tag,attrs):
        data=dict(attrs)
        if tag in {'script','style','noscript','svg'}: self._skip+=1
        if tag=='title': self._in_title=True
        if tag=='meta' and data.get('name','').lower() in {'description','og:description'}: self.description=data.get('content','')
        if tag=='a' and data.get('href'): self.links.append(data['href'])
    def handle_endtag(self,tag):
        if tag in {'script','style','noscript','svg'} and self._skip: self._skip-=1
        if tag=='title': self._in_title=False
    def handle_data(self,data):
        value=' '.join(unescape(data).split())
        if not value or self._skip: return
        if self._in_title: self.title=(self.title+' '+value).strip()
        self.text.append(value)

def validate_public_url(url):
    parsed=urlparse(url)
    if parsed.scheme not in {'http','https'} or not parsed.hostname or parsed.username or parsed.password:
        raise CheckFailure('Enter a public HTTP or HTTPS website URL.')
    host=parsed.hostname.lower()
    if host in {'localhost','localhost.localdomain'} or host.endswith('.local'):
        raise CheckFailure('Private or local website addresses are not allowed.')
    try: address=ipaddress.ip_address(host)
    except ValueError: address=None
    if address is not None and not address.is_global:
        raise CheckFailure('Private or reserved website addresses are not allowed.')
    return parsed

class WebsiteIntelligence:
    def __init__(self,store): self.store=store

    def _get(self,url):
        validate_public_url(url)
        response=httpx.get(url,headers={'User-Agent':'AI-Marketing-Manager/1.0 WebsiteIntelligence'},
                           timeout=15,follow_redirects=False)
        if 300 <= response.status_code < 400:
            location=response.headers.get('location')
            if not location: raise CheckFailure('Website returned an invalid redirect.')
            target=urljoin(url,location); original=validate_public_url(url); redirected=validate_public_url(target)
            if redirected.hostname!=original.hostname: raise CheckFailure('Cross-domain redirects are not followed during website ingestion.')
            response=httpx.get(target,headers={'User-Agent':'AI-Marketing-Manager/1.0 WebsiteIntelligence'},timeout=15,follow_redirects=False)
        response.raise_for_status()
        if len(response.content)>2_000_000: raise CheckFailure('Website page is too large to ingest safely.')
        return response

    def scan(self,root_url,max_pages=12):
        root=validate_public_url(root_url); base=f'{root.scheme}://{root.netloc}'
        urls=[root_url.rstrip('/') or base]
        try:
            sitemap=self._get(urljoin(base,'/sitemap.xml'))
            if 'xml' in sitemap.headers.get('content-type','') or sitemap.text.lstrip().startswith('<?xml'):
                tree=ElementTree.fromstring(sitemap.content)
                for element in tree.iter():
                    if element.tag.endswith('loc') and element.text:
                        candidate=element.text.strip(); parsed=validate_public_url(candidate)
                        if parsed.hostname==root.hostname and candidate not in urls: urls.append(candidate)
        except Exception: pass
        pages=[]; candidate_items=[]
        for url in urls[:max(1,min(max_pages,25))]:
            response=self._get(url)
            if 'text/html' not in response.headers.get('content-type','text/html'): continue
            parser=_PageParser(); parser.feed(response.text)
            text=' '.join(parser.text)[:12000]
            suspicious=any(re.search(pattern,text,re.I) for pattern in INJECTION_PATTERNS)
            digest=hashlib.sha256((url+'\n'+text).encode()).hexdigest()
            page={'url':url,'title':parser.title[:500] or url,'description':parser.description[:1200],
                  'content_hash':digest,'retrieved_at':time.time(),'suspicious':suspicious,'text_excerpt':text[:2500]}
            pages.append(page)
            summary=parser.description or ' '.join(parser.text[:8])
            if summary:
                candidate_items.append({'kind':'website_summary','key':url,'value':summary[:2500],
                                        'source_url':url,'evidence':text[:1200],'confidence':0.75 if not suspicious else 0.2,
                                        'sensitivity':'public','status':'discovered','content_hash':digest})
            for match in re.finditer(r'(?i)(?:₹|INR|USD|EUR|GBP|\$|€|£)\s?[0-9][0-9,.]*(?:\s?(?:per|/)[a-z]+)?',text):
                candidate_items.append({'kind':'price_candidate','key':url+'#price-'+str(match.start()),'value':match.group(0)[:120],
                                        'source_url':url,'evidence':text[max(0,match.start()-100):match.end()+100],
                                        'confidence':0.65,'sensitivity':'public','status':'discovered','content_hash':digest})
        return self.store.save_website_scan(root_url,pages,candidate_items)
