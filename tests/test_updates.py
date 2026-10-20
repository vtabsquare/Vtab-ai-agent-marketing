import hashlib
import hmac
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.store import Store
from app.controller import Controller
from app.agents import AgentRegistry
from app.tools import PublisherBot, CheckFailure
from app.integrations import Channel
from app.providers import PROVIDERS, DemoProvider

ROOT=Path(__file__).resolve().parents[1]
BRIEF={'title':'Campaign','audience':'Founders','goal':'Introduce our brand','instructions':''}

def draft(store,controller):
    c=controller.create(BRIEF)
    for _ in range(25):
        controller.step(); c=store.get(c['id'])
        if c['state']=='AWAITING_APPROVAL': return c
    raise AssertionError(c['state'])

def test_credentials_are_encrypted_and_hidden(tmp_path):
    app=create_app(tmp_path,False)
    with TestClient(app) as client:
        s=client.get('/api/settings').json()
        response=client.put('/api/settings',json={'brand':s['brand'],'social_keys':{'hf_token':'hf-private-secret','linkedin_author':'urn:li:person:123'}})
        assert response.status_code==200
        assert 'hf-private-secret' not in response.text
        assert response.json()['configured_integrations']['hf_token']
        assert 'hf-private-secret' not in app.state.store.path.read_bytes().decode(errors='ignore')
        client.put('/api/settings',json={'brand':s['brand']})
        assert app.state.store.settings()['social_keys']['hf_token']=='hf-private-secret'
        client.put('/api/settings',json={'brand':s['brand'],'social_keys':{'hf_token':''}})
        assert app.state.store.settings()['social_keys']['hf_token']==''

def test_concurrent_writers_and_readers(tmp_path):
    store=Store(tmp_path); controller=Controller(store,AgentRegistry(ROOT)); c=controller.create(BRIEF)
    def change(i):
        store.mutate(c['id'],lambda row:row['events'].append({'test':i}))
        return store.get(c['id'])['version']
    with ThreadPoolExecutor(max_workers=8) as pool: list(pool.map(change,range(40)))
    assert store.get(c['id'])['version']==41
    assert store.connect().execute('PRAGMA busy_timeout').fetchone()[0]==30000

def test_live_schedule_survives_restart_and_uses_real_metrics(tmp_path,monkeypatch):
    store=Store(tmp_path); settings=store.settings(); settings.update(publishing_mode='live',platforms=['twitter']); store.set_settings(settings)
    monkeypatch.setattr(Channel,'publish',lambda self,text,*args,**kwargs:{'platform':'twitter','post_id':'123','status':'published'})
    monkeypatch.setattr(Channel,'metrics',lambda self,post_id:{'available':True,'impressions':500,'engagement_rate_pct':8,'platform':'twitter'})
    controller=Controller(store,AgentRegistry(ROOT)); c=draft(store,controller)
    controller.approve(c['id'],{'content_hash':c['content_hash'],'note':''}); controller.step()
    waiting=store.get(c['id']); assert waiting['state']=='SCHEDULED_WAIT'
    assert waiting['nodes']['analytics']['not_before']>=time.time()+86390
    restored=Store(tmp_path); assert restored.claim() is None
    restored.mutate(c['id'],lambda row:row['nodes']['analytics'].update(not_before=0))
    resumed=Controller(restored,AgentRegistry(ROOT)); resumed.step()
    measured=restored.get(c['id'])['results']['analytics']['metrics']
    assert measured['mode']=='live' and measured['impressions']==500

def test_publication_ledger_prevents_duplicate_and_unknown_retry(tmp_path,monkeypatch):
    store=Store(tmp_path); s=store.settings(); s.update(publishing_mode='live',platforms=['discord']); store.set_settings(s)
    c=draft(store,Controller(store,AgentRegistry(ROOT))); calls=[]
    monkeypatch.setattr(Channel,'publish',lambda self,text,*args,**kwargs:calls.append(text) or {'platform':'discord','post_id':'1','status':'published'})
    publisher=PublisherBot(store)
    first=publisher.publish(c,c['content_hash']); assert publisher.publish(c,c['content_hash'])==first; assert len(calls)==1
    with store.transaction() as db: db.execute("UPDATE publications SET status='submitting'")
    with pytest.raises(CheckFailure): publisher.publish(c,c['content_hash'])
    assert len(calls)==1

def test_signed_webhook_queue_and_approval(tmp_path,monkeypatch):
    secret='a'*40; monkeypatch.setenv('MARKETING_WEBHOOK_SECRET',secret)
    app=create_app(tmp_path,False); store=app.state.store; c=app.state.controller.create(BRIEF)
    store.mutate(c['id'],lambda row:row['results'].update(publishing={'output':{'receipts':[{'platform':'twitter','post_id':'42'}]}}))
    body=json.dumps({'event_id':'event-1','campaign_id':c['id'],'platform':'twitter','post_id':'42','author':'Alice','text':'What is the price?'}).encode()
    stamp=str(int(time.time())); signature=hmac.new(secret.encode(),stamp.encode()+b'.'+body,hashlib.sha256).hexdigest()
    headers={'x-marketing-timestamp':stamp,'x-marketing-signature':signature,'content-type':'application/json'}
    with TestClient(app) as client:
        assert client.post('/api/webhooks/engagement',content=body).status_code==401
        assert client.post('/api/webhooks/engagement',content=body,headers=headers).status_code==202
        assert client.post('/api/webhooks/engagement',content=body,headers=headers).status_code==202
        assert len(app.state.community.list())==1
        assert app.state.community.step()
        item=client.get('/api/engagement').json()[0]; assert item['state']=='AWAITING_APPROVAL'
        assert client.post('/api/engagement/'+item['id']+'/decision',json={'draft_hash':'0'*64,'approve':True}).status_code==409
        assert client.post('/api/engagement/'+item['id']+'/decision',json={'draft_hash':item['draft_hash'],'approve':True}).json()['state']=='APPROVED'

def test_server_requires_login_and_own_origin(tmp_path,monkeypatch):
    monkeypatch.setenv('MARKETING_MODE','server'); monkeypatch.setenv('MARKETING_ADMIN_PASSWORD','long-client-password')
    monkeypatch.setenv('MARKETING_ALLOWED_HOSTS','testserver,client.example'); monkeypatch.setenv('MARKETING_ALLOWED_ORIGINS','https://client.example')
    with TestClient(create_app(tmp_path,False)) as client:
        assert client.get('/api/settings').status_code==401
        assert client.get('/api/health').status_code==200
        assert client.get('/api/settings',auth=('admin','long-client-password')).status_code==200
        assert client.post('/api/campaigns',json=BRIEF,auth=('admin','long-client-password'),headers={'origin':'https://client.example'}).status_code==201
        assert client.post('/api/campaigns',json=BRIEF,auth=('admin','long-client-password'),headers={'origin':'https://evil.example'}).status_code==403

def test_brand_review_cannot_be_bypassed(tmp_path,monkeypatch):
    class Unsafe(DemoProvider):
        def generate(self,request):
            result=super().generate(request)
            if request.role=='brand_review': result.output.update(verdict='revise',summary='Unsupported guarantee')
            return result
    monkeypatch.setitem(PROVIDERS,'demo',lambda model,key:Unsafe())
    store=Store(tmp_path); controller=Controller(store,AgentRegistry(ROOT)); c=controller.create(BRIEF)
    for _ in range(35): controller.step()
    result=store.get(c['id']); assert result['state']=='BLOCKED'; assert 'publishing' not in result['results']

def test_preview_does_not_call_image_service(tmp_path,monkeypatch):
    import httpx
    monkeypatch.setattr(httpx,'get',lambda *a,**k:pytest.fail('Preview made a network request'))
    app=create_app(tmp_path,False); c=draft(app.state.store,app.state.controller)
    with TestClient(app) as client:
        assert client.get('/api/campaigns/'+c['id']+'/creative.svg').status_code==200

def test_unexpected_server_exception_is_json(tmp_path,monkeypatch):
    app=create_app(tmp_path,False)
    monkeypatch.setattr(app.state.store,'list',lambda:(_ for _ in ()).throw(RuntimeError('sensitive details')))
    with TestClient(app) as client:
        response=client.get('/api/campaigns')
        assert response.status_code==500 and 'application/json' in response.headers['content-type']
        assert 'sensitive details' not in response.text

def test_discord_receipt_is_real_and_mentions_disabled(monkeypatch):
    import httpx
    calls=[]
    def post(url,**kwargs):
        calls.append((url,kwargs))
        return httpx.Response(200,json={'id':'actual-message','channel_id':'channel'},request=httpx.Request('POST',url))
    monkeypatch.setattr(httpx,'post',post)
    receipt=Channel('discord',{'discord_webhook':'https://discord.com/api/webhooks/123/test-token'}).publish('Hello')
    assert receipt['post_id']=='actual-message'
    assert calls[0][1]['params']=={'wait':'true'}
    assert calls[0][1]['json']['allowed_mentions']=={'parse':[]}
    with pytest.raises(CheckFailure): Channel('discord',{'discord_webhook':'http://127.0.0.1/private'}).publish('Hello')
    assert len(calls)==1

def test_x_uses_user_token_and_platform_metrics(monkeypatch):
    import httpx
    def post(url,**kwargs):
        assert url=='https://api.x.com/2/tweets'
        assert kwargs['headers']['Authorization']=='Bearer user-token'
        return httpx.Response(201,json={'data':{'id':'42'}},request=httpx.Request('POST',url))
    def get(url,**kwargs):
        return httpx.Response(200,json={'data':{'public_metrics':{'like_count':10,'reply_count':2}}},request=httpx.Request('GET',url))
    monkeypatch.setattr(httpx,'post',post); monkeypatch.setattr(httpx,'get',get)
    channel=Channel('twitter',{'twitter_access_token':'user-token'})
    assert channel.publish('Hello')['post_id']=='42'
    metrics=channel.metrics('42'); assert metrics['impressions'] is None and metrics['engagement_rate_pct'] is None
    assert metrics['engagements']==12

def test_linkedin_receipt_and_author(monkeypatch):
    import httpx
    def post(url,**kwargs):
        assert url=='https://api.linkedin.com/rest/posts'
        assert kwargs['json']['author']=='urn:li:person:123'
        return httpx.Response(201,headers={'x-restli-id':'urn:li:share:42'},request=httpx.Request('POST',url))
    monkeypatch.setattr(httpx,'post',post)
    channel=Channel('linkedin',{'linkedin_token':'token','linkedin_author':'urn:li:person:123'})
    assert channel.publish('Hello')['post_id']=='urn:li:share:42'
    assert channel.metrics('urn:li:share:42')['available'] is False

def test_huggingface_uses_campaign_prompt_without_generic_suffix(monkeypatch):
    from app import integrations
    from PIL import Image
    calls=[]
    class Client:
        def __init__(self,**kwargs): calls.append(kwargs)
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def text_to_image(self,prompt,**kwargs):
            calls.append((prompt,kwargs)); return Image.new('RGB',(16,16),'navy')
    monkeypatch.setattr(integrations,'InferenceClient',Client)
    result=integrations.generate_image('A specific still life',{'image_provider':'huggingface','hf_model':'black-forest-labs/FLUX.1-schnell'},{'social_keys':{'hf_token':'hf-token'}})
    assert result.startswith('data:image/png;base64,')
    assert calls[0]['api_key']=='hf-token' and calls[1][0]=='A specific still life'

def test_native_x_callback_checks_signatures_and_queues_replies(tmp_path,monkeypatch):
    import base64
    app=create_app(tmp_path,False); store=app.state.store
    s=store.settings(); s['social_keys']={'twitter_client_secret':'oauth-secret'}; store.set_settings(s)
    c=app.state.controller.create(BRIEF)
    store.mutate(c['id'],lambda row:row['results'].update(publishing={'output':{'receipts':[{'platform':'twitter','post_id':'42'}]}}))
    body=json.dumps({'data':{'event_type':'post.reply.create','event_uuid':'event123','payload':{'id':'43','in_reply_to_tweet_id':'42','author_id':'customer','text':'Tell me more'}}}).encode()
    signature='sha256='+base64.b64encode(hmac.new(b'oauth-secret',body,hashlib.sha256).digest()).decode()
    with TestClient(app) as client:
        expected='sha256='+base64.b64encode(hmac.new(b'oauth-secret',b'challenge',hashlib.sha256).digest()).decode()
        assert client.get('/api/webhooks/x?crc_token=challenge').json()['response_token']==expected
        assert client.post('/api/webhooks/x',content=body).status_code==503
        headers={'x-twitter-webhooks-signature-oauth2':signature}
        assert client.post('/api/webhooks/x',content=body,headers=headers).json()['matched_replies']==1
        assert client.post('/api/webhooks/x',content=body,headers=headers).status_code==200
        assert len(app.state.community.list())==1
