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


def test_writing_contract_accepts_rich_offer_prices_and_empty_variant_headlines():
    from app.contracts import Writing
    payload = {
        "headline": "Grand Opening SS Hyderabad Biryani Tiruvallur",
        "caption": "Enjoy authentic Hyderabadi biryani with our Buy 2 Get 1 FREE Grand Opening offer at ₹99!",
        "product_claim": "Authentic Hyderabadi Chicken Biryani, Mutton Biryani, and Bucket Biryani in Chennai and Tamil Nadu",
        "price_claim": "Smile Pack from ₹99. Grand Opening offer: Buy 2 Chicken Biryani, Get 1 FREE",
        "call_to_action": "Order via WhatsApp at +91 76007 44444",
        "variants": [
            {"channel": "whatsapp", "body": "Order your favourite biryani now! Buy 2 Get 1 FREE."},
            {"channel": "instagram", "headline": "", "body": "Tiruvallur branch is now OPEN! Taste the love of sharing."}
        ]
    }
    validated = Writing.model_validate(payload)
    assert validated.price_claim.startswith("Smile Pack")
    assert validated.variants[0].headline == ""


def test_gemini_provider_handles_markdown_and_heals_missing_fields(monkeypatch):
    import types
    from google import genai
    from app.contracts import Writing

    markdown_response = '```json\n{"headline": "SS Biryani Feast", "caption": "Delicious food at ₹99", "variants": [{"channel": "whatsapp", "body": "Text us!"}]}\n```'

    class Client:
        def __init__(self, **kw):
            self.models = types.SimpleNamespace(
                generate_content=lambda **kw: types.SimpleNamespace(
                    text=markdown_response,
                    usage_metadata=types.SimpleNamespace(prompt_token_count=10, candidates_token_count=20)
                )
            )
        def close(self): pass

    monkeypatch.setattr(genai, "Client", Client)
    provider = GeminiProvider("gemini-test", "test-key")
    ctx = {"brand": {"product": "Bucket Biryani", "price": "₹99"}}
    res = provider.generate(ModelRequest("writing", ctx, Writing, "writing.v2"))
    assert res.output["headline"] == "SS Biryani Feast"
    assert res.output["product_claim"] == "Bucket Biryani"
    assert res.output["price_claim"] == "₹99"
    assert res.output["variants"][0]["channel"] == "whatsapp"




def test_bandwidth_logging_middleware(tmp_path, caplog):
    import logging
    with caplog.at_level(logging.INFO, logger="bandwidth"):
        with TestClient(create_app(tmp_path, start_worker=False)) as client:
            res = client.get("/api/health")
            assert res.status_code == 200
    assert any("http_request method=GET path=/api/health status=200" in record.message for record in caplog.records)
