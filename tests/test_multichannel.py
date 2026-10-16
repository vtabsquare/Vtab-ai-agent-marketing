from fastapi.testclient import TestClient
from app.main import create_app

def test_campaign_selects_content_only_destinations_without_live_publish(tmp_path):
    app=create_app(tmp_path,start_worker=False)
    with TestClient(app) as client:
        settings=client.get('/api/settings').json()
        payload={k:settings[k] for k in ('provider','model','brand','channel_settings','data_mode')}
        payload['channel_settings']['instagram']={'mode':'content_only','enabled':True}
        payload['publishing_mode']='live'
        assert client.put('/api/settings',json=payload).status_code==200
        campaign=client.post('/api/campaigns',json={'title':'Launch','audience':'Buyers','goal':'Awareness','destinations':['instagram']}).json()
        assert campaign['snapshot']['publishing']=='simulation'
        assert campaign['snapshot']['configuration']['destinations']==[{'channel':'instagram','state':'content_only'}]

def test_unavailable_destination_is_rejected(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        response=client.post('/api/campaigns',json={'title':'Launch','audience':'Buyers','goal':'Awareness','destinations':['instagram']})
        assert response.status_code==409
