from starlette.testclient import TestClient
from app.main import create_app


def test_audit_trail_flow(tmp_path):
    app = create_app(tmp_path, start_worker=False)
    client = TestClient(app)

    # 1. Create a campaign
    brief = {
        'title': 'Audit Test Campaign',
        'goal': 'Verify audit trail logging',
        'audience': 'Developers',
        'instructions': 'Test only',
        'checkpoint': 'none'
    }
    resp = client.post('/api/campaigns', json=brief)
    assert resp.status_code == 201

    # 2. Check audit trail captured creation with method and path
    audit_resp = client.get('/api/audit')
    assert audit_resp.status_code == 200
    events = audit_resp.json()
    assert isinstance(events, list)
    assert any(e.get('path') == '/api/campaigns' and e.get('method') == 'POST' for e in events)
