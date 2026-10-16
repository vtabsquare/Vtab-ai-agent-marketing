from fastapi.testclient import TestClient
from app.main import create_app

def test_standalone_catalog_audience_and_lead_lifecycle(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        product=client.post('/api/catalog',json={'name':'Solar Kit','kind':'product','price':'INR 2,499'}).json()
        assert product['name']=='Solar Kit' and len(client.get('/api/catalog').json())==1
        audience=client.post('/api/audiences',json={'name':'Home owners','description':'Local energy-conscious households'}).json()
        assert audience['language']=='en'
        lead=client.post('/api/leads',json={'name':'Asha','email':'asha@example.com','consent_status':'granted'}).json()
        assert lead['status']=='new'
        duplicate=client.post('/api/leads',json={'name':'Asha 2','email':'ASHA@example.com'})
        assert duplicate.status_code==409
        updated=client.put('/api/leads/'+lead['id'],json={'status':'qualified','note':'Requested a demo'}).json()
        assert updated['status']=='qualified' and updated['notes'][0]['text']=='Requested a demo'
        assert client.delete('/api/leads/'+lead['id']).json()['deleted']

def test_csv_import_reports_duplicates_without_losing_valid_rows(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        csv_text='Full Name,Email\nAsha,asha@example.com\nDuplicate,asha@example.com\nRavi,ravi@example.com\n'
        result=client.post('/api/imports/leads',json={'csv_text':csv_text,'mapping':{'Full Name':'name','Email':'email'}}).json()
        assert result['created']==2 and result['errors'][0]['row']==3
        assert len(client.get('/api/leads').json())==2
