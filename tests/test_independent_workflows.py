import threading
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.store import Store,Conflict
from app.agents import AgentRegistry
from app.controller import Controller
from app.providers import DemoProvider,PROVIDERS
from test_workflow import system, BRIEF, ROOT, until_pause


def test_two_workflows_really_execute_concurrently(system,monkeypatch):
    store,controller=system
    barrier=threading.Barrier(2)
    seen=[]
    class Concurrent(DemoProvider):
        def generate(self,request):
            seen.append(request.context['brief']['title'])
            barrier.wait(timeout=3)
            return super().generate(request)
    monkeypatch.setitem(PROVIDERS,'demo',lambda model,key:Concurrent())
    a=controller.create({**BRIEF,'title':'Workflow A'})
    b=controller.create({**BRIEF,'title':'Workflow B'})
    with ThreadPoolExecutor(2) as pool:
        futures=[pool.submit(controller.step) for _ in range(2)]
        assert all(f.result(timeout=5) for f in futures)
    assert set(seen)=={'Workflow A','Workflow B'}
    assert store.get(a['id'])['nodes']['research']['state']=='ACCEPTED'
    assert store.get(b['id'])['nodes']['research']['state']=='ACCEPTED'


def test_sibling_bots_parallel_results_merge_without_lost_update(system,monkeypatch):
    store,controller=system
    c=controller.create(BRIEF)
    controller.step();controller.step()
    barrier=threading.Barrier(2)
    roles=[]
    class Siblings(DemoProvider):
        def generate(self,request):
            roles.append(request.role)
            barrier.wait(timeout=3)
            return super().generate(request)
    monkeypatch.setitem(PROVIDERS,'demo',lambda model,key:Siblings())
    with ThreadPoolExecutor(2) as pool:
        futures=[pool.submit(controller.step) for _ in range(2)]
        assert all(f.result(timeout=5) for f in futures)
    merged=store.get(c['id'])
    assert set(roles)=={'writing','creative'}
    assert merged['nodes']['writing']['state']==merged['nodes']['creative']['state']=='ACCEPTED'
    assert set(merged['results'])=={'research','strategy','writing','creative'}
    assert len([t for t in merged['tasks'] if t['status']=='ACCEPTED'])==4


def test_bot_waits_for_answer_while_other_workflow_proceeds(system):
    store,controller=system
    a=controller.create({**BRIEF,'title':'Needs direction','checkpoint':'creative'})
    b=controller.create({**BRIEF,'title':'Automatic','checkpoint':'none'})
    for _ in range(20): controller.step()
    waiting=store.get(a['id']);other=store.get(b['id'])
    assert waiting['nodes']['creative']['state']=='WAITING_INPUT'
    assert waiting['nodes']['writing']['state']=='ACCEPTED'
    assert other['state']=='AWAITING_APPROVAL'
    q=next(q for q in waiting['input_requests'] if q['status']=='OPEN')
    controller.answer(a['id'],{'request_id':q['id'],'answer':'Use an indigo and purple visual style.'})
    resumed=until_pause(store,controller,a['id'])
    assert resumed['state']=='AWAITING_APPROVAL'
    assert resumed['results']['creative']['output']['primary_hex']=='#312e81'
    assert resumed['human_answers']['creative'][0]['answer'].startswith('Use an indigo')
    assert store.get(b['id'])['state']=='AWAITING_APPROVAL'
    with pytest.raises(Conflict):controller.answer(a['id'],{'request_id':q['id'],'answer':'Duplicate answer'})


def test_provider_can_request_input_and_receive_answer(system,monkeypatch):
    store,controller=system
    class Questions(DemoProvider):
        def generate(self,request):
            response=super().generate(request)
            if request.role=='research' and not request.context['human_answers']:
                response.output['input_request']={'question':'Which audience should I prioritize?','reason':'I need clarification to proceed.'}
            return response
    monkeypatch.setitem(PROVIDERS,'demo',lambda model,key:Questions())
    c=controller.create(BRIEF);controller.step()
    c=store.get(c['id']);assert c['state']=='WAITING_INPUT'
    assert 'research' not in c['results']
    controller.answer(c['id'],{'request_id':c['input_requests'][0]['id'],'answer':'First-time business owners'})
    controller.step()
    assert store.get(c['id'])['nodes']['research']['state']=='ACCEPTED'


def test_global_pool_limit_and_claim_exclusion(system):
    store,controller=system
    for _ in range(5):controller.create(BRIEF)
    claims=[store.claim() for _ in range(4)]
    assert len({c['id'] for c,t in claims})==4
    assert store.claim() is None


def test_notification_is_scoped_and_resolves_after_answer(tmp_path):
    app=create_app(tmp_path,start_worker=False)
    with TestClient(app) as client:
        c=client.post('/api/campaigns',json={**BRIEF,'checkpoint':'creative'}).json()
        until_pause(app.state.store,app.state.controller,c['id'])
        ns=client.get('/api/notifications').json()
        assert len(ns)==1 and ns[0]['campaign_id']==c['id'] and ns[0]['role']=='creative'
        assert client.post('/api/campaigns/'+c['id']+'/input',json={'request_id':ns[0]['id'],'answer':'Warm amber colors'}).status_code==200
        assert client.get('/api/notifications').json()==[]
        assert client.post('/api/campaigns/'+c['id']+'/input',json={'request_id':ns[0]['id'],'answer':'Duplicate'}).status_code==409


def test_cancelled_workflow_cannot_accept_answer(system):
    store,controller=system
    c=controller.create({**BRIEF,'checkpoint':'creative'})
    waiting=until_pause(store,controller,c['id'])
    q=waiting['input_requests'][0]
    controller.cancel(c['id'])
    with pytest.raises(Conflict):controller.answer(c['id'],{'request_id':q['id'],'answer':'Too late'})


def test_old_sibling_result_is_discarded_after_revision(system):
    store,controller=system
    c=controller.create(BRIEF);controller.step();controller.step()
    writer,writer_token=store.claim();creative,creative_token=store.claim()
    assert writer['_task']['role']=='writing' and creative['_task']['role']=='creative'
    store.mutate(c['id'],lambda row:controller.reset_content(row,'Correct the approved facts.'))
    assert store.complete(c['id'],creative_token,lambda row,t,n:row['results'].update(creative={'output':{'headline':'STALE'}})) is False
    assert 'creative' not in store.get(c['id'])['results']


def test_existing_sequential_database_migrates_without_data_loss(tmp_path):
    store=Store(tmp_path);controller=Controller(store,AgentRegistry(ROOT))
    c=controller.create(BRIEF);ready=until_pause(store,controller,c['id'])
    def legacy(row):
        row.pop('nodes');row.pop('input_requests');row.pop('human_answers')
    store.mutate(c['id'],legacy)
    restored=Store(tmp_path).get(c['id'])
    assert restored['state']=='AWAITING_APPROVAL'
    assert restored['content_hash']==ready['content_hash']
    assert restored['input_requests'][0]['kind']=='approval'
    assert restored['nodes']['writing']['state']=='ACCEPTED'
