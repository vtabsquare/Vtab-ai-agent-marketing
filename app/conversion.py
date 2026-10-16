"""Hosted conversion pages, forms, attribution links and event capture."""
import html
import json
import re
import secrets
import time
import uuid
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl
from .store import Missing, Conflict

class ConversionService:
    def __init__(self,store): self.store=store
    def create_page(self,data):
        slug=re.sub(r'[^a-z0-9-]+','-',data['slug'].strip().lower()).strip('-')
        if not slug: raise Conflict('Landing-page slug is invalid.')
        now=time.time(); page={**data,'id':uuid.uuid4().hex,'slug':slug,'form_token':secrets.token_urlsafe(24),
                               'created_at':now,'updated_at':now,'status':'draft'}
        try:
            with self.store.transaction() as db: db.execute('INSERT INTO landing_pages VALUES(?,?,?,?,?,?)',(page['id'],slug,page['form_token'],page['status'],now,json.dumps(page)))
        except Exception as exc:
            if 'UNIQUE' in str(exc).upper(): raise Conflict('This landing-page slug is already in use.') from None
            raise
        return page
    def list_pages(self):
        with self.store.reading() as db: rows=db.execute('SELECT payload FROM landing_pages ORDER BY updated_at DESC').fetchall()
        return [json.loads(row[0]) for row in rows]
    def publish(self,page_id):
        with self.store.transaction() as db:
            row=db.execute('SELECT payload FROM landing_pages WHERE id=?',(page_id,)).fetchone()
            if not row: raise Missing('Landing page not found.')
            page=json.loads(row[0]); page.update(status='published',updated_at=time.time())
            db.execute('UPDATE landing_pages SET status=?,updated_at=?,payload=? WHERE id=?',('published',page['updated_at'],json.dumps(page),page_id))
        return page
    def get_public(self,slug):
        with self.store.reading() as db: row=db.execute("SELECT payload FROM landing_pages WHERE slug=? AND status='published'",(slug,)).fetchone()
        if not row: raise Missing('Landing page not found.')
        return json.loads(row[0])
    def get_by_token(self,token):
        with self.store.reading() as db: row=db.execute("SELECT payload FROM landing_pages WHERE form_token=? AND status='published'",(token,)).fetchone()
        if not row: raise Missing('Lead form not found.')
        return json.loads(row[0])
    def render(self,page):
        title=html.escape(page['title']); body=html.escape(page['body']).replace('\n','<br>'); cta=html.escape(page['cta_label'])
        return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>body{{margin:0;font-family:Inter,Arial,sans-serif;background:#f5f3ff;color:#17122b}}main{{max-width:760px;margin:7vh auto;padding:48px;background:white;border-radius:28px;box-shadow:0 30px 80px #3b1b7a22}}h1{{font-size:clamp(2.3rem,7vw,4.8rem);line-height:1;margin:.2em 0}}p{{font-size:1.1rem;line-height:1.7}}form{{display:grid;gap:14px;margin-top:30px}}input,textarea{{padding:15px;border:1px solid #d9d3ef;border-radius:12px;font:inherit}}button{{padding:16px;border:0;border-radius:14px;background:linear-gradient(135deg,#6d3df5,#9b5cf6);color:white;font-weight:700;box-shadow:0 14px 30px #6d3df544}}.hp{{position:absolute;left:-9999px}}</style></head><body><main><small>{html.escape(page.get('eyebrow',''))}</small><h1>{title}</h1><p>{body}</p><form method="post" action="/public/forms/{page['form_token']}/submit"><input name="name" placeholder="Your name"><input name="email" type="email" placeholder="Email"><input name="phone" placeholder="Phone"><textarea name="message" placeholder="How can we help?"></textarea><label><input type="checkbox" name="consent" value="granted" required> I agree to be contacted about this request.</label><input class="hp" name="website" tabindex="-1" autocomplete="off"><button>{cta}</button></form></main></body></html>'''
    @staticmethod
    def utm_url(url,source,medium,campaign,content=''):
        parsed=urlparse(url)
        if parsed.scheme not in {'http','https'} or not parsed.netloc: raise Conflict('Enter a valid destination URL.')
        query=dict(parse_qsl(parsed.query,keep_blank_values=True)); query.update(utm_source=source,utm_medium=medium,utm_campaign=campaign)
        if content: query['utm_content']=content
        return urlunparse(parsed._replace(query=urlencode(query)))
    def event(self,event_type,source,campaign_id=None,metadata=None):
        now=time.time(); event={'id':uuid.uuid4().hex,'event_type':event_type,'source':source,'campaign_id':campaign_id,
                                 'metadata':metadata or {},'occurred_at':now}
        with self.store.transaction() as db: db.execute('INSERT INTO metric_events VALUES(?,?,?,?,?,?)',(event['id'],event_type,source,campaign_id,now,json.dumps(event)))
        return event
