import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.workflow_registry import WorkflowRegistry

ROOT=Path(__file__).resolve().parents[1]

def test_registry_validates_and_lists_capability_gated_workflows(tmp_path):
    registry=WorkflowRegistry(ROOT)
    definitions=registry.available({'campaigns.create','content.generate'})
    assert next(item for item in definitions if item['id']=='campaign.v1')['available']
    assert not next(item for item in definitions if item['id']=='website-growth.v1')['available']

def test_registry_rejects_cycles(tmp_path):
    config=tmp_path/'config'; config.mkdir()
    (config/'workflows.json').write_text(json.dumps({'version':1,'default':'bad','workflows':{'bad':{
        'name':'Bad','description':'Bad','roles':['research','strategy'],
        'dependencies':{'research':['strategy'],'strategy':['research']},'required_capabilities':[]}}}))
    with pytest.raises(ValueError): WorkflowRegistry(tmp_path)

def test_workflow_api_and_snapshot_version(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        definitions=client.get('/api/workflow-definitions').json()
        assert len(definitions)>=2
        campaign=client.post('/api/campaigns',json={'title':'Launch','audience':'Buyers','goal':'Awareness','workflow_id':'campaign.v1'}).json()
        assert campaign['snapshot']['workflow']['id']=='campaign.v1'
