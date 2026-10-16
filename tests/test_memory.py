from fastapi.testclient import TestClient
from app.main import create_app
from app.memory import MemoryService
from app.store import Store

def record(scope,status='approved',content='Approved concise headlines for founders'):
    return {'scope':scope,'memory_type':'approved_pattern','content':content,'source':'owner','source_id':None,
            'confidence':0.9,'status':status,'sensitivity':'internal','tags':['founders','headline'],
            'expires_at':None,'prompt_version':None,'model_version':None,'supersedes_id':None}

def test_memory_scopes_and_candidate_governance(tmp_path):
    service=MemoryService(Store(tmp_path))
    client=service.create(record('client'))
    writer=service.create(record('agent.writing'))
    research=service.create(record('agent.research'))
    candidate=service.create(record('agent.writing','candidate','Untested idea'))
    found=service.retrieve('writing','abc','founders headline')
    ids={item['id'] for item in found}
    assert {client['id'],writer['id']} <= ids
    assert research['id'] not in ids and candidate['id'] not in ids

def test_memory_api_supports_approval_supersession_and_deletion(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        first=client.post('/api/memories',json=record('client','candidate')).json()
        assert client.post('/api/memories/'+first['id']+'/decision',json={'status':'approved','note':'Verified'}).json()['status']=='approved'
        second_payload=record('client','approved','New approved pattern'); second_payload['supersedes_id']=first['id']
        second=client.post('/api/memories',json=second_payload).json()
        memories=client.get('/api/memories').json()
        assert next(item for item in memories if item['id']==first['id'])['status']=='superseded'
        assert client.delete('/api/memories/'+second['id']).json()['deleted']
