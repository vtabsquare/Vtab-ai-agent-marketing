import copy
import hashlib
import json
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.agents import AgentRegistry, IMPLEMENTATIONS, Specialist
from app.controller import Controller, fingerprint
from app.providers import DemoProvider, ModelResponse, ProviderError, PROVIDERS
from app.store import Store, Conflict
from app.tools import content_hash, validate_copy, CheckFailure, brand_card, metrics_fixture

ROOT = Path(__file__).resolve().parents[1]
BRIEF = {"title": "Launch campaign", "audience": "Small business owners", "goal": "Introduce the package", "instructions": ""}


@pytest.fixture
def system(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    store = Store(tmp_path)
    controller = Controller(store, AgentRegistry(ROOT))
    return store, controller


def until_pause(store, controller, campaign_id):
    for _ in range(35):
        c = store.get(campaign_id)
        if c["state"] not in {"QUEUED", "RUNNING", "RETRY_SCHEDULED"}:
            return c
        controller.step()
    raise AssertionError("Workflow did not pause within its limits")


def draft(system):
    store, controller = system
    c = controller.create(BRIEF)
    return until_pause(store, controller, c["id"])


def test_complete_campaign_checks_all_roles(system):
    store, controller = system
    c = draft(system)
    assert c["state"] == "AWAITING_APPROVAL"
    assert "publishing" not in c["results"]
    assert controller.step() is False
    controller.approve(c["id"], {"content_hash": c["content_hash"], "note": "Looks good"})
    done = until_pause(store, controller, c["id"])
    assert done["state"] == "COMPLETED"
    assert len(done["tasks"]) == 10
    assert all(t["status"] == "ACCEPTED" for t in done["tasks"])
    assert done["results"]["publishing"]["output"]["status"] == "confirmed_simulated"
    assert done["results"]["engagement"]["output"]["requires_human"]
    assert done["model_calls"] == 9


def test_no_approval_before_review(system):
    store, controller = system
    c = controller.create(BRIEF)
    with pytest.raises(Conflict):
        controller.approve(c["id"], {"content_hash": "0"*64, "note": ""})


def test_stale_hash_cannot_authorize(system):
    c = draft(system)
    with pytest.raises(Conflict):
        system[1].approve(c["id"], {"content_hash": "0"*64, "note": ""})


def test_revision_invalidates_approval_and_reruns_review(system):
    store, controller = system
    c = draft(system)
    controller.revise(c["id"], {"content_hash": c["content_hash"], "note": "Make the introduction clearer"})
    revised = until_pause(store, controller, c["id"])
    assert revised["state"] == "AWAITING_APPROVAL"
    assert revised["approval"] is None
    assert revised["revisions"] == 1
    assert sum(t["role"] == "brand_review" for t in revised["tasks"]) == 2


def test_changed_content_is_not_published(system):
    store, controller = system
    c = draft(system)
    controller.approve(c["id"], {"content_hash": c["content_hash"], "note": ""})
    store.mutate(c["id"], lambda row: row["results"]["writing"]["output"].update(caption="Tampered"))
    controller.step()
    assert store.get(c["id"])["state"] == "BLOCKED"
    assert "publishing" not in store.get(c["id"])["results"]


def test_missing_approval_cannot_publish(system):
    store, controller = system
    c = draft(system)
    store.mutate(c["id"], lambda row: row.update(state="QUEUED"))
    assert controller.step() is False
    assert 'publishing' not in store.get(c['id'])['results']


def test_simulator_identity_prevents_duplicate_receipts(system):
    c = draft(system)
    publisher = system[1].publisher
    assert publisher.publish(c, c["content_hash"]) == publisher.publish(c, c["content_hash"])


def test_cancellation_discards_inflight_result(system):
    store, controller = system
    c = controller.create(BRIEF)
    claimed, token = store.claim()
    controller.cancel(c["id"])
    claimed["state"] = "COMPLETED"
    assert store.complete(c['id'], token, lambda row,task,node: row.update(state='COMPLETED')) is False
    assert store.get(c["id"])["state"] == "CANCELLED"


def test_expired_lease_resumes_saved_step(system):
    store, controller = system
    c = controller.create(BRIEF)
    store.claim()
    assert store.claim() is None
    store.mutate(c['id'], lambda row: row['nodes']['research'].update(lease_until=0))
    controller.step()
    recovered = store.get(c["id"])
    assert recovered["stage"] == 1
    assert recovered["tasks"][0]["status"] == "INTERRUPTED"
    assert recovered["model_calls"] == 2


def test_restart_retains_approval_wait(system):
    store, controller = system
    c = draft(system)
    restored = Store(store.folder)
    assert restored.get(c["id"])["state"] == "AWAITING_APPROVAL"
    assert restored.claim() is None


def test_gemini_setup_gate_and_no_secret_in_export(system):
    store, controller = system
    s = store.settings()
    s.update(provider="gemini", model="test-model", tested_fingerprint="")
    store.set_settings(s, "secret-local-key")
    with pytest.raises(Conflict):
        controller.create(BRIEF)
    s["tested_fingerprint"] = fingerprint(s, "secret-local-key")
    store.set_settings(s)
    c = controller.create(BRIEF)
    assert "secret-local-key" not in json.dumps(c)
    assert c["snapshot"]["agents"]["profiles"]["default"]["model"] == "test-model"


def test_campaign_keeps_model_and_brand_snapshot(system):
    store, controller = system
    c = controller.create(BRIEF)
    s = store.settings()
    s["brand"]["price"] = "INR 9,999"
    s.update(provider="gemini", model="different-model")
    store.set_settings(s)
    done = until_pause(store, controller, c["id"])
    assert done["state"] == "AWAITING_APPROVAL"
    assert done["results"]["writing"]["provider"] == "demo"
    assert done["results"]["writing"]["output"]["price_claim"] == "INR 2,499"


def test_bad_price_is_revised_with_bound(system, monkeypatch):
    class WrongPrice(DemoProvider):
        def generate(self, request):
            result = super().generate(request)
            if request.role == "writing":
                result.output["price_claim"] = "INR 1"
            return result
    monkeypatch.setitem(PROVIDERS, "demo", lambda model,key: WrongPrice())
    c = draft(system)
    assert c["state"] == "BLOCKED"
    assert c["revisions"] == 2
    assert "publishing" not in c["results"]


def test_successful_revision_after_wrong_price(system, monkeypatch):
    calls = []
    class OneBadPrice(DemoProvider):
        def generate(self, request):
            result = super().generate(request)
            if request.role == "writing":
                calls.append(request.context)
                if len(calls) == 1:
                    result.output["price_claim"] = "INR 1"
            return result
    monkeypatch.setitem(PROVIDERS, "demo", lambda model,key: OneBadPrice())
    c = draft(system)
    assert c["state"] == "AWAITING_APPROVAL"
    assert c["revisions"] == 1
    assert calls[1]["revision_note"]


def test_quota_stops_without_repeated_diagnosis(system, monkeypatch):
    class Exhausted(DemoProvider):
        def generate(self, request):
            raise ProviderError("Quota reached", kind="quota")
    monkeypatch.setitem(PROVIDERS, "demo", lambda model,key: Exhausted())
    c = draft(system)
    assert c["state"] == "BLOCKED"
    assert c["model_calls"] == 1


def test_transient_retry_limit(system, monkeypatch):
    class Unavailable(DemoProvider):
        def generate(self, request):
            raise ProviderError("Connection failed", retryable=True, kind="connection")
    monkeypatch.setitem(PROVIDERS, "demo", lambda model,key: Unavailable())
    store, controller = system
    c = controller.create(BRIEF)
    for i in range(3):
        controller.step()
        store.mutate(c["id"], lambda row: row['nodes']['research'].update(not_before=0))
    assert store.get(c["id"])["state"] == "BLOCKED"
    assert len(store.get(c["id"])["tasks"]) == 3


def test_agent_can_be_replaced_without_workflow_edit(system, monkeypatch):
    class Replacement(Specialist):
        def run(self, context, provider, schema, configuration, timeout):
            result = super().run(context,provider,schema,configuration,timeout)
            result.output["summary"] = "Replacement strategy accepted."
            return result
    monkeypatch.setitem(IMPLEMENTATIONS,"strategy_v1",lambda: Replacement("strategy"))
    c = draft(system)
    assert c["results"]["strategy"]["output"]["summary"] == "Replacement strategy accepted."


def test_source_links_cannot_be_invented(system, monkeypatch):
    class Invented(DemoProvider):
        def generate(self, request):
            result = super().generate(request)
            if request.role == "research":
                result.output["findings"][0]["source_ref"] = "https://invented.example"
            return result
    monkeypatch.setitem(PROVIDERS,"demo",lambda model,key:Invented())
    assert draft(system)["state"] == "BLOCKED"


def test_model_budget_stops_dispatch(system):
    store, controller = system
    c = controller.create(BRIEF)
    store.mutate(c["id"],lambda row:row["snapshot"]["agents"]["limits"].update(max_model_calls=1))
    blocked = until_pause(store,controller,c["id"])
    assert blocked["state"] == "BLOCKED"
    assert blocked["error"]["kind"] == "budget"


def test_caption_conflicting_price_is_rejected(system):
    c = draft(system)
    output = dict(c["results"]["writing"]["output"])
    output["caption"] += " Discount price: INR 1."
    with pytest.raises(CheckFailure):
        validate_copy(output,c["snapshot"]["brand"])


def test_svg_escapes_model_markup(system):
    c = draft(system)
    c["results"]["creative"]["output"]["headline"] = "<script>alert(1)</script>"
    svg = brand_card(c)
    assert "<script>" not in svg
    assert "&lt;script&gt;" in svg


def test_metrics_calculated_by_code():
    assert metrics_fixture()["engagement_rate_pct"] == 5
    assert metrics_fixture()["click_through_rate_pct"] == 2


def test_api_blocks_cross_origin_mutation(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        response = client.post('/api/campaigns',json=BRIEF,headers={"Origin":"https://evil.example"})
        assert response.status_code == 403
        assert client.get('/api/campaigns').json() == []


def test_api_settings_test_and_export_hide_key(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        s = client.get('/api/settings').json()
        payload = {k:s[k] for k in ['provider','model','brand']}
        payload["api_key"] = "secret-only-local"
        response = client.put('/api/settings',json=payload)
        assert response.status_code == 200
        assert "secret-only-local" not in response.text
        assert client.post('/api/settings/test').status_code == 200
        c = client.post('/api/campaigns',json=BRIEF).json()
        exported = client.get('/api/campaigns/'+c['id']+'/export')
        assert "secret-only-local" not in exported.text
        assert client.get('/').status_code == 200
        assert client.get('/api/campaigns/not-real').status_code == 404


def test_api_rejects_unknown_live_provider(tmp_path):
    with TestClient(create_app(tmp_path,start_worker=False)) as client:
        s = client.get('/api/settings').json()
        payload = {"provider":"unknown","model":"x","brand":s['brand']}
        assert client.put('/api/settings',json=payload).status_code == 422


def test_api_approval_complete_and_svg(tmp_path):
    app = create_app(tmp_path,start_worker=False)
    with TestClient(app) as client:
        c = client.post('/api/campaigns',json=BRIEF).json()
        ready = until_pause(app.state.store,app.state.controller,c['id'])
        assert client.get('/api/campaigns/'+c['id']+'/creative.svg').status_code == 200
        response = client.post('/api/campaigns/'+c['id']+'/approve',json={"content_hash":ready['content_hash'],"note":""})
        assert response.status_code == 200
        assert until_pause(app.state.store,app.state.controller,c['id'])['state'] == 'COMPLETED'
