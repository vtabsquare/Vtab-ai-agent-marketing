from fastapi.testclient import TestClient
from app.main import create_app

def configure(client,access_mode='read_only'):
    settings=client.get('/api/settings').json()
    payload={k:settings[k] for k in ('provider','model','brand','channel_settings')}
    payload.update(data_mode='hybrid',connectors=[{'id':'crm-main','type':'generic_crm','enabled':True,
        'access_mode':access_mode,'capabilities':['crm.read','crm.write'],'ownership_domains':['contacts','segments']}])
    assert client.put('/api/settings',json=payload).status_code==200

def test_connector_sync_is_idempotent_and_dead_letters_invalid_records(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        configure(client)
        payload={'records':[{'entity_type':'contact','external_id':'c-1','fields':{'email':'a@example.com'}},
                            {'entity_type':'contact','external_id':'','fields':{}}],'cursor':'next-1'}
        first=client.post('/api/connectors/crm-main/sync',json=payload).json()
        assert first['created']==1 and first['errors']==1
        second=client.post('/api/connectors/crm-main/sync',json={'records':[payload['records'][0]],'cursor':'next-2'}).json()
        assert second['updated']==1 and len(client.get('/api/connectors/crm-main/records?entity_type=contact').json())==1

def test_connector_writes_require_read_write_mode(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        configure(client,'read_only')
        body={'entity_type':'contact','external_id':'c-1','operation':'update','fields':{'status':'qualified'},'approved_by':'owner'}
        assert client.post('/api/connectors/crm-main/outbox',json=body).status_code==409
        configure(client,'read_write')
        assert client.post('/api/connectors/crm-main/outbox',json=body).status_code==202
