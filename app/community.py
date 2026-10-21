"""Durable normalized webhook inbox; replies stay drafts until a person approves."""
import hashlib
import json
import re
import time
from .contracts import Contract, Field
from .store import Conflict, Missing
from .providers import get_key


class Comment(Contract):
    event_id: str = Field(min_length=1,max_length=150)
    campaign_id: str = Field(min_length=1,max_length=100)
    platform: str = Field(pattern=r'^(discord|twitter|linkedin|facebook|instagram|whatsapp)$')
    post_id: str = Field(min_length=1,max_length=200)
    author: str = Field(min_length=1,max_length=200)
    text: str = Field(min_length=1,max_length=3000)


class ReplyDecision(Contract):
    draft_hash: str = Field(pattern=r'^[a-f0-9]{64}$')
    approve: bool


class Community:
    def __init__(self,store,registry,mailer=None):
        self.store,self.registry=store,registry
        from .mailer import MailerService
        self.mailer=mailer or MailerService(self.store)

    def list(self):
        with self.store.reading() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT payload FROM engagement').fetchall()]

    def receive(self, data):
        c=self.store.get(data['campaign_id'])
        receipts=c.get('results',{}).get('publishing',{}).get('output',{}).get('receipts',[])
        def _match_post(r):
            if r.get('platform') != data['platform']: return False
            if data['platform'] == 'whatsapp': return True
            rp, dp = str(r.get('post_id','')), str(data.get('post_id',''))
            return rp == dp or rp.endswith('_'+dp) or dp.endswith('_'+rp.split('_')[-1]) or rp in dp or dp in rp
        if not any(_match_post(r) for r in receipts):
            raise Conflict('Comment does not match a confirmed campaign publication.')
        event=hashlib.sha256((data['platform']+':'+data['event_id']).encode()).hexdigest()
        item={'id':event,**data,'state':'QUEUED','created_at':time.time(),'attempts':0,'lease_until':0,'not_before':0}
        with self.store.transaction() as db:
            db.execute('INSERT OR IGNORE INTO engagement VALUES(?,?)',(event,json.dumps(item)))
            created=json.loads(db.execute('SELECT payload FROM engagement WHERE id=?',(event,)).fetchone()[0])
        try:
            self.mailer.send_comment_received(created)
        except Exception:
            pass
        return created

    def decide(self,event,data):
        with self.store.transaction() as db:
            row=db.execute('SELECT payload FROM engagement WHERE id=?',(event,)).fetchone()
            if not row: raise Missing('Reply not found.')
            item=json.loads(row[0])
            if item['state']!='AWAITING_APPROVAL' or data['draft_hash']!=item.get('draft_hash'):
                raise Conflict('Review the current reply before deciding.')
            approved = data['approve']
            item.update(state='APPROVED' if approved else 'REJECTED',reviewed_at=time.time())
            db.execute('UPDATE engagement SET payload=? WHERE id=?',(json.dumps(item),event))

        # If approved and platform is Facebook, post the reply to the comment thread
        if approved and item.get('platform') == 'facebook':
            try:
                draft_reply = item.get('output', {}).get('draft_reply', '')
                if draft_reply:
                    keys = self.store.settings().get('social_keys', {})
                    page_token = keys.get('facebook_page_token', '')
                    comment_id = item.get('event_id', '')  # event_id = Facebook comment_id
                    if page_token and comment_id:
                        import httpx
                        target_id = comment_id
                        resp = httpx.post(
                            f'https://graph.facebook.com/v21.0/{target_id}/comments',
                            data={'message': draft_reply, 'access_token': page_token},
                            timeout=30
                        )
                        if resp.status_code >= 400 and item.get('post_id') and target_id != item.get('post_id'):
                            fallback_resp = httpx.post(
                                f"https://graph.facebook.com/v21.0/{item.get('post_id')}/comments",
                                data={'message': draft_reply, 'access_token': page_token},
                                timeout=30
                            )
                            if fallback_resp.status_code < 400:
                                resp = fallback_resp
                        resp.raise_for_status()
                        reply_id = resp.json().get('id', '')
                        with self.store.transaction() as db:
                            row = db.execute('SELECT payload FROM engagement WHERE id=?',(event,)).fetchone()
                            if row:
                                updated = json.loads(row[0])
                                updated['facebook_reply_id'] = reply_id
                                updated['facebook_reply_posted'] = True
                                db.execute('UPDATE engagement SET payload=? WHERE id=?',(json.dumps(updated),event))
                        item['facebook_reply_id'] = reply_id
                        item['facebook_reply_posted'] = True
            except Exception as e:
                # Don't fail the approval if posting back fails — log it in the item
                with self.store.transaction() as db:
                    row = db.execute('SELECT payload FROM engagement WHERE id=?',(event,)).fetchone()
                    if row:
                        updated = json.loads(row[0])
                        updated['facebook_reply_error'] = str(e)[:300]
                        db.execute('UPDATE engagement SET payload=? WHERE id=?',(json.dumps(updated),event))
                item['facebook_reply_error'] = str(e)[:300]

        # If approved and platform is Instagram, post the reply to the comment thread
        if approved and item.get('platform') == 'instagram':
            try:
                draft_reply = item.get('output', {}).get('draft_reply', '')
                if draft_reply:
                    keys = self.store.settings().get('social_keys', {})
                    token = keys.get('instagram_access_token') or keys.get('facebook_page_token', '')
                    comment_id = item.get('event_id', '')  # event_id = Instagram comment_id
                    if token and comment_id:
                        import httpx
                        resp = httpx.post(
                            f'https://graph.facebook.com/v21.0/{comment_id}/replies',
                            data={'message': draft_reply, 'access_token': token},
                            timeout=30
                        )
                        resp.raise_for_status()
                        reply_id = resp.json().get('id', '')
                        with self.store.transaction() as db:
                            row = db.execute('SELECT payload FROM engagement WHERE id=?',(event,)).fetchone()
                            if row:
                                updated = json.loads(row[0])
                                updated['instagram_reply_id'] = reply_id
                                updated['instagram_reply_posted'] = True
                                db.execute('UPDATE engagement SET payload=? WHERE id=?',(json.dumps(updated),event))
                        item['instagram_reply_id'] = reply_id
                        item['instagram_reply_posted'] = True
            except Exception as e:
                with self.store.transaction() as db:
                    row = db.execute('SELECT payload FROM engagement WHERE id=?',(event,)).fetchone()
                    if row:
                        updated = json.loads(row[0])
                        updated['instagram_reply_error'] = str(e)[:300]
                        db.execute('UPDATE engagement SET payload=? WHERE id=?',(json.dumps(updated),event))
                item['instagram_reply_error'] = str(e)[:300]

        # If approved and platform is WhatsApp, send reply message via WhatsApp Cloud API
        if approved and item.get('platform') == 'whatsapp':
            try:
                draft_reply = item.get('output', {}).get('draft_reply', '')
                if draft_reply:
                    keys = self.store.settings().get('social_keys', {})
                    phone_number_id = keys.get('whatsapp_phone_number_id', '')
                    token = keys.get('whatsapp_token', '') or keys.get('facebook_page_token', '')
                    recipient = item.get('author_phone') or item.get('post_id') or keys.get('whatsapp_recipient', '')
                    clean_recipient = re.sub(r'[^\d]', '', str(recipient))
                    if phone_number_id and token and clean_recipient:
                        import httpx
                        resp = httpx.post(
                            f'https://graph.facebook.com/v21.0/{phone_number_id}/messages',
                            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                            json={
                                'messaging_product': 'whatsapp',
                                'recipient_type': 'individual',
                                'to': clean_recipient,
                                'type': 'text',
                                'text': {'preview_url': False, 'body': draft_reply}
                            },
                            timeout=30
                        )
                        resp.raise_for_status()
                        reply_id = resp.json().get('messages', [{}])[0].get('id', '')
                        with self.store.transaction() as db:
                            row = db.execute('SELECT payload FROM engagement WHERE id=?',(event,)).fetchone()
                            if row:
                                updated = json.loads(row[0])
                                updated['whatsapp_reply_id'] = reply_id
                                updated['whatsapp_reply_posted'] = True
                                db.execute('UPDATE engagement SET payload=? WHERE id=?',(json.dumps(updated),event))
                        item['whatsapp_reply_id'] = reply_id
                        item['whatsapp_reply_posted'] = True
            except Exception as e:
                with self.store.transaction() as db:
                    row = db.execute('SELECT payload FROM engagement WHERE id=?',(event,)).fetchone()
                    if row:
                        updated = json.loads(row[0])
                        updated['whatsapp_reply_error'] = str(e)[:300]
                        db.execute('UPDATE engagement SET payload=? WHERE id=?',(json.dumps(updated),event))
                item['whatsapp_reply_error'] = str(e)[:300]

        if approved:
            try:
                draft_reply = item.get('output', {}).get('draft_reply', '')
                reply_id = item.get('facebook_reply_id') or item.get('instagram_reply_id') or item.get('whatsapp_reply_id') or item.get('event_id')
                self.mailer.send_reply_posted(item, draft_reply, reply_id)
            except Exception:
                pass
        return item

    def sync_social_comments(self):
        """Polls connected Instagram and Facebook posts for new comments and queues them."""
        import httpx
        keys = self.store.settings().get('social_keys', {})
        ig_token = keys.get('instagram_access_token') or keys.get('facebook_page_token', '')
        fb_token = keys.get('facebook_page_token', '')
        queued = 0

        existing_events = set()
        with self.store.reading() as db:
            for row in db.execute('SELECT payload FROM engagement').fetchall():
                payload = json.loads(row[0])
                existing_events.add(str(payload.get('event_id', '')))

        for c in self.store.recent(limit=3):
            receipts = c.get('results', {}).get('publishing', {}).get('output', {}).get('receipts', [])
            for r in receipts:
                platform = r.get('platform')
                post_id = r.get('post_id')
                if not post_id:
                    continue

                # 1. Instagram comments
                if platform == 'instagram' and ig_token:
                    try:
                        resp = httpx.get(
                            f'https://graph.facebook.com/v21.0/{post_id}/comments?fields=id,text,from,timestamp&access_token={ig_token}',
                            timeout=15
                        )
                        if resp.status_code == 200:
                            for item in resp.json().get('data', []):
                                cid = str(item.get('id', ''))
                                if cid and cid not in existing_events:
                                    text = item.get('text', '').strip()
                                    author = item.get('from', {}).get('username') or 'Instagram User'
                                    try:
                                        self.receive({
                                            'event_id': cid,
                                            'campaign_id': c['id'],
                                            'platform': 'instagram',
                                            'post_id': str(post_id),
                                            'author': author,
                                            'text': text
                                        })
                                        existing_events.add(cid)
                                        queued += 1
                                    except Exception:
                                        pass
                    except Exception:
                        pass

                # 2. Facebook comments — independent check (NOT elif, so campaigns with both IG+FB receipts poll both)
                if platform == 'facebook' and fb_token:
                    try:
                        resp = httpx.get(
                            f'https://graph.facebook.com/v21.0/{post_id}/comments?fields=id,message,from,created_time&access_token={fb_token}',
                            timeout=15
                        )
                        if resp.status_code == 200:
                            for item in resp.json().get('data', []):
                                cid = str(item.get('id', ''))
                                if cid and cid not in existing_events:
                                    text = item.get('message', '').strip()
                                    author = item.get('from', {}).get('name') or 'Facebook User'
                                    try:
                                        self.receive({
                                            'event_id': cid,
                                            'campaign_id': c['id'],
                                            'platform': 'facebook',
                                            'post_id': str(post_id),
                                            'author': author,
                                            'text': text
                                        })
                                        existing_events.add(cid)
                                        queued += 1
                                    except Exception:
                                        pass
                    except Exception:
                        pass

                # 3. WhatsApp — poll inbound messages received by the business number
                if platform == 'whatsapp':
                    wa_token = keys.get('whatsapp_token') or keys.get('facebook_page_token', '')
                    phone_number_id = keys.get('whatsapp_phone_number_id', '')
                    if wa_token and phone_number_id:
                        try:
                            import json as _json
                            filter_param = _json.dumps([{"field": "status", "operator": "EQUAL", "value": "received"}])
                            resp = httpx.get(
                                f'https://graph.facebook.com/v21.0/{phone_number_id}/messages',
                                params={'fields': 'id,from,text,timestamp,type', 'filtering': filter_param, 'access_token': wa_token},
                                timeout=15
                            )
                            if resp.status_code == 200:
                                for msg in resp.json().get('data', []):
                                    mid = str(msg.get('id', ''))
                                    if not mid or mid in existing_events:
                                        continue
                                    if msg.get('type', '') != 'text':
                                        continue
                                    text = (msg.get('text') or {}).get('body', '').strip()
                                    from_num = str(msg.get('from', ''))
                                    author = f'+{from_num}' if from_num else 'WhatsApp User'
                                    if not text:
                                        continue
                                    try:
                                        self.receive({
                                            'event_id': mid,
                                            'campaign_id': c['id'],
                                            'platform': 'whatsapp',
                                            'post_id': from_num or post_id,
                                            'author': author,
                                            'text': text
                                        })
                                        existing_events.add(mid)
                                        queued += 1
                                    except Exception:
                                        pass
                        except Exception:
                            pass

        return queued

    def step(self):
        # Auto-poll social comments every 45 seconds
        now = time.time()
        if getattr(self, '_last_sync', 0) + 45 < now:
            self._last_sync = now
            try:
                self.sync_social_comments()
            except Exception:
                pass

        with self.store.transaction() as db:
            item=None
            for row in db.execute('SELECT payload FROM engagement').fetchall():
                candidate=json.loads(row[0])
                if candidate['not_before']>time.time(): continue
                if candidate['state']=='QUEUED' or (candidate['state']=='RUNNING' and candidate['lease_until']<time.time()):
                    item=candidate; break
            if item is None: return False
            item.update(state='RUNNING',lease_until=time.time()+120,attempts=item['attempts']+1)
            db.execute('UPDATE engagement SET payload=? WHERE id=?',(json.dumps(item),item['id']))
        try:
            campaign=self.store.get(item['campaign_id']); cfg=campaign['snapshot']['agents']
            result=self.registry.run('engagement',{'brand':campaign['snapshot']['brand'],'brief':campaign['brief'],
                'feedback':item['text'],'author':item['author'],'mode':'live','human_answers':[]},cfg,get_key(self.store))
            draft=result['output']; draft['requires_human']=True
            from .controller import redact
            for secret in [get_key(self.store),*self.store.settings().get('social_keys',{}).values()]: draft=redact(draft,secret)
            item.update(state='AWAITING_APPROVAL',output=draft,draft_hash=hashlib.sha256(json.dumps(draft,sort_keys=True).encode()).hexdigest())
        except Exception:
            item.update(state='QUEUED' if item['attempts']<3 else 'BLOCKED',not_before=time.time()+30,
                        error='Community reply could not be drafted. Check the model configuration.')
        with self.store.transaction() as db:
            db.execute('UPDATE engagement SET payload=? WHERE id=?',(json.dumps(item),item['id']))
        return True
