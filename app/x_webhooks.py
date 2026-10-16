"""X Activity reply events and legacy Account Activity reply events."""
import base64
import hashlib
import hmac
import json
from fastapi import HTTPException, Request
from .community import Comment


def register_x_webhooks(app,store,community):
    @app.get('/api/webhooks/x')
    def challenge(crc_token: str):
        if len(crc_token)>500: raise HTTPException(400,'Invalid challenge.')
        keys=store.settings().get('social_keys',{})
        secret=keys.get('twitter_client_secret') or keys.get('twitter_api_secret')
        if not secret: raise HTTPException(503,'Configure the X webhook signing secret.')
        digest=hmac.new(secret.encode(),crc_token.encode(),hashlib.sha256).digest()
        return {'response_token':'sha256='+base64.b64encode(digest).decode()}

    @app.post('/api/webhooks/x')
    async def events(request: Request):
        keys=store.settings().get('social_keys',{})
        oauth2=request.headers.get('x-twitter-webhooks-signature-oauth2')
        signature=oauth2 or request.headers.get('x-twitter-webhooks-signature','')
        secret=keys.get('twitter_client_secret') if oauth2 else keys.get('twitter_api_secret')
        if not secret: raise HTTPException(503,'Configure the matching X webhook signing secret.')
        chunks=[];size=0
        async for chunk in request.stream():
            size+=len(chunk)
            if size>1_000_000: raise HTTPException(413,'Webhook payload too large.')
            chunks.append(chunk)
        body=b''.join(chunks)
        expected='sha256='+base64.b64encode(hmac.new(secret.encode(),body,hashlib.sha256).digest()).decode()
        if not hmac.compare_digest(signature,expected): raise HTTPException(401,'Invalid X webhook signature.')
        try:
            payload=json.loads(body)
            if not isinstance(payload,dict): raise ValueError()
        except ValueError: raise HTTPException(400,'Invalid event payload.') from None
        incoming=[]
        event=payload.get('data',{})
        if isinstance(event,dict) and event.get('event_type')=='post.reply.create':
            post=event.get('payload',{})
            if isinstance(post,dict):
                incoming.append((str(event.get('event_uuid') or post.get('id','')),post))
        legacy=payload.get('tweet_create_events',[])
        if isinstance(legacy,list):
            incoming.extend((str(p.get('id_str') or p.get('id','')),p) for p in legacy if isinstance(p,dict))
        campaigns=store.list();queued=0
        for event_id,post in incoming:
            parent=post.get('in_reply_to_tweet_id') or post.get('in_reply_to_status_id_str') or post.get('in_reply_to_status_id')
            if not parent:
                refs=post.get('referenced_tweets',[])
                parent=next((r.get('id') for r in refs if isinstance(r,dict) and r.get('type')=='replied_to'),None)
            if not parent: continue
            parent=str(parent)
            campaign=next((c for c in campaigns if any(r.get('platform')=='twitter' and r.get('post_id')==parent for r in c.get('results',{}).get('publishing',{}).get('output',{}).get('receipts',[]))),None)
            if not campaign: continue
            user=post.get('user',{})
            if not isinstance(user,dict): user={}
            try:
                comment=Comment.model_validate({'event_id':event_id,'campaign_id':campaign['id'],'platform':'twitter',
                    'post_id':parent,'author':str(user.get('screen_name') or post.get('author_id') or 'X user'),
                    'text':post.get('full_text') or post.get('text') or ''})
            except ValueError: raise HTTPException(422,'The reply event is missing required fields.') from None
            community.receive(comment.model_dump());queued+=1
        return {'ok':True,'matched_replies':queued}
