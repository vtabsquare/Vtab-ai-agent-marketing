from fastapi.testclient import TestClient
from app.main import create_app

def test_funnel_and_experiment_lifecycle(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        for event in ['page_view','page_view','form_submit','conversion']:
            assert client.post('/api/public/events',json={'event_type':event,'source':'website','campaign_id':'campaign-1'}).status_code==202
        funnel=client.get('/api/analytics/funnel?campaign_id=campaign-1').json()
        assert funnel['lead_conversion_pct']==50 and funnel['customer_conversion_pct']==100
        experiment=client.post('/api/experiments',json={'name':'CTA test','campaign_id':'campaign-1','hypothesis':'Direct CTA improves leads',
            'metric':'form_submit','stop_rule':'Stop after 200 exposures','variants':[
                {'id':'control','name':'Control','description':'Request details'},
                {'id':'direct','name':'Direct','description':'Book a consultation'}]}).json()
        client.post('/api/experiments/'+experiment['id']+'/results',json={'variant':'control','exposures':100,'conversions':5})
        result=client.post('/api/experiments/'+experiment['id']+'/results',json={'variant':'direct','exposures':100,'conversions':8}).json()
        assert result['analysis']['leader']=='direct' and result['analysis']['difference_pct_points']==3
        assert client.post('/api/experiments/'+experiment['id']+'/complete').json()['status']=='completed'
