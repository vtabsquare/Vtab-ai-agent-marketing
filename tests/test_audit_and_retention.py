from starlette.testclient import TestClient
from app.main import create_app


def test_audit_and_retention_flow(tmp_path):
    app = create_app(tmp_path, start_worker=False)
    client = TestClient(app)

    # 1. Create a campaign
    brief = {
        'title': 'Retention Test Campaign',
        'goal': 'Verify deletion of completed workflows',
        'audience': 'Developers',
        'instructions': 'Test only',
        'checkpoint': 'none'
    }
    resp = client.post('/api/campaigns', json=brief)
    assert resp.status_code == 201
    camp = resp.json()
    camp_id = camp['id']

    # 2. Check audit trail captured creation
    audit_resp = client.get('/api/audit')
    assert audit_resp.status_code == 200
    events = audit_resp.json()
    assert isinstance(events, list)
    assert any(e.get('path') == '/api/campaigns' and e.get('method') == 'POST' for e in events)

    # 3. Attempting to delete an active campaign should fail with 409 Conflict
    del_resp = client.delete(f'/api/campaigns/{camp_id}')
    assert del_resp.status_code == 409
    assert 'Active workflows cannot be deleted' in del_resp.json()['detail']

    # 4. Cancel the campaign to allow deletion
    cancel_resp = client.post(f'/api/campaigns/{camp_id}/cancel')
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()['state'] == 'CANCELLED'

    # 5. Deleting the cancelled campaign now succeeds
    del_resp = client.delete(f'/api/campaigns/{camp_id}')
    assert del_resp.status_code == 200
    assert del_resp.json() == {'deleted': True, 'id': camp_id}

    # 6. Deleting again returns 404 Missing
    del_resp2 = client.delete(f'/api/campaigns/{camp_id}')
    assert del_resp2.status_code == 404
