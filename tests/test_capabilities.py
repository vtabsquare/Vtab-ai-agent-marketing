from fastapi.testclient import TestClient
from app.capabilities import effective_capabilities, normalize_settings, workflow_configuration_snapshot
from app.main import create_app

def test_legacy_settings_normalize_to_standalone_without_enabling_live_channels():
    settings=normalize_settings({'platforms':[]})
    assert settings['data_mode']=='standalone'
    assert settings['channel_settings']['linkedin']['mode']=='disabled'
    assert settings['channel_settings']['web_export']['mode']=='content_only'

def test_three_modes_and_channel_capabilities_are_explicit():
    settings=normalize_settings({'data_mode':'hybrid','platforms':[],
        'channel_settings':{'instagram':{'mode':'content_only','enabled':True},'facebook':{'mode':'fully_connected','enabled':True}},
        'connectors':[{'id':'crm-main','type':'crm','enabled':True,'capabilities':['crm.read']}]})
    result=effective_capabilities(settings)
    assert result['mode']['name']=='Hybrid'
    assert 'content.channel.instagram' in result['capabilities'] and 'publish.instagram' not in result['capabilities']
    assert {'publish.facebook','metrics.facebook','crm.read'} <= set(result['capabilities'])

def test_workflow_snapshot_preserves_mode_and_destinations():
    snapshot=workflow_configuration_snapshot(normalize_settings({'data_mode':'standalone','platforms':['twitter']}))
    assert snapshot['data_mode']=='standalone'
    assert {'channel':'twitter','state':'publishing_connected'} in snapshot['destinations']

def test_capabilities_api_and_campaign_snapshot(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        assert client.get('/api/capabilities').json()['data_mode']=='standalone'
        campaign=client.post('/api/campaigns',json={'title':'Website launch','audience':'Local buyers','goal':'Generate enquiries','instructions':''}).json()
        assert campaign['snapshot']['configuration']['data_mode']=='standalone'
