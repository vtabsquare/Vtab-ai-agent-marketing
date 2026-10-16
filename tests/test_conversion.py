from fastapi.testclient import TestClient
from app.main import create_app

def test_landing_page_lead_capture_and_utm(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        page=client.post('/api/landing-pages',json={'slug':'Solar Launch','title':'Meet Solar Kit','body':'Power your next project.','cta_label':'Request details'}).json()
        assert client.get('/forms/solar-launch').status_code==404
        assert client.post('/api/landing-pages/'+page['id']+'/publish').status_code==200
        html=client.get('/forms/solar-launch')
        assert html.status_code==200 and 'Meet Solar Kit' in html.text and page['form_token'] in html.text
        submitted=client.post('/public/forms/'+page['form_token']+'/submit',data={'name':'Asha','email':'asha@example.com','consent':'granted'}).json()
        assert submitted['accepted'] and client.get('/api/leads').json()[0]['consent_status']=='granted'
        utm=client.post('/api/utm',json={'url':'https://example.com/product','source':'instagram','medium':'social','campaign':'solar-launch'}).json()['url']
        assert 'utm_source=instagram' in utm and 'utm_campaign=solar-launch' in utm
