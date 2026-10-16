import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient
from app.contracts import Strategy
from app.main import create_app
from app.providers import GeminiProvider, ModelRequest, ProviderError, SYSTEM, build_provider

ROOT = Path(__file__).resolve().parents[1]


def test_shared_system_prompt_includes_role_specific_tuning():
    assert "summarize and synthesize live_web_search results" in SYSTEM
    assert "weave factual information naturally into a compelling story" in SYSTEM
    assert "engagements and impressions metrics against past campaign data" in SYSTEM

def test_gemini_receives_versioned_role_instructions(monkeypatch):
    from google import genai
    calls=[]
    class Response:
        text=json.dumps({'summary':'Strategy','content_angle':'Angle','success_measure':'Measure'})
        usage_metadata=None
    class Models:
        def generate_content(self,**kwargs): calls.append(kwargs); return Response()
    class Client:
        def __init__(self,**kwargs): self.models=Models()
        def close(self): pass
    monkeypatch.setattr(genai,'Client',Client)
    GeminiProvider('model','key').generate(ModelRequest('strategy',{},Strategy,'strategy.v2',45,'Role-specific instruction.'))
    assert 'Role-specific instruction.' in calls[0]['config'].system_instruction


def test_gemini_sdk_contract_with_mocked_transport(monkeypatch):
    from google import genai
    calls = []
    class Response:
        text = json.dumps({"summary":"Strategy","content_angle":"Clear offer","success_measure":"Confirmed result"})
        usage_metadata = None
    class Models:
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            return Response()
    class Client:
        def __init__(self, **kwargs):
            self.models = Models()
        def close(self):
            calls.append("closed")
    monkeypatch.setattr(genai,"Client",Client)
    provider = GeminiProvider("configured-model","test-key")
    result = provider.generate(ModelRequest("strategy",{},Strategy,"strategy.v1"))
    assert result.output["summary"] == "Strategy"
    assert calls[0]["model"] == "configured-model"
    assert calls[0]["config"].response_mime_type == "application/json"
    assert calls[-1] == "closed"


def test_unknown_provider_fails_clearly():
    try:
        build_provider({"provider":"not-installed","model":"x"},"")
    except ProviderError as exc:
        assert exc.kind == "configuration"
    else:
        raise AssertionError("Unknown adapter should fail")


def test_launcher_help_runs_without_third_party_imports():
    result = subprocess.run([sys.executable,str(ROOT/'deploy.py'),'--help'],capture_output=True,text=True)
    assert result.returncode == 0
    assert "--no-browser" in result.stdout


def test_launcher_reports_invalid_port():
    result = subprocess.run([sys.executable,str(ROOT/'deploy.py'),'--port','1','--no-install'],capture_output=True,text=True)
    assert result.returncode != 0
    assert "Choose a port" in result.stderr


def test_validation_does_not_echo_key(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        response = client.put('/api/settings',json={"api_key":"secret-do-not-echo"*30})
        assert response.status_code == 422
        assert "secret-do-not-echo" not in response.text
