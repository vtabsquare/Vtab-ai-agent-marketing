from fastapi.testclient import TestClient
from app.main import create_app
from app.store import Store


def test_pilot_demo_portal_and_headers():
    client = TestClient(create_app(), cookies={})
    resp = client.get('/demo')
    assert resp.status_code == 200
    assert 'marketing_session' in resp.cookies
    csp = resp.headers.get('content-security-policy', '')
    assert "frame-ancestors 'self' https://vtabsquare.com" in csp
    assert 'https://www.vtabsquare.com' in csp


def test_pilot_demo_auth_and_simulation_lock():
    client = TestClient(create_app(), cookies={})
    
    # 1. Pilot login
    auth_resp = client.post('/api/auth/demo')
    assert auth_resp.status_code == 200
    data = auth_resp.json()
    assert data['authenticated'] is True
    assert data['user']['is_pilot'] is True
    assert data['user']['email'] == 'demo@vtabsquare.com'
    session_cookie = auth_resp.cookies.get('marketing_session')
    assert session_cookie is not None

    # 2. Authenticated requests with pilot session
    demo_client = TestClient(create_app(), cookies={'marketing_session': session_cookie})
    me_resp = demo_client.get('/api/auth/me')
    assert me_resp.status_code == 200
    assert me_resp.json()['user']['is_pilot'] is True

    # 3. Create campaign must strictly force simulated publishing
    campaign_resp = demo_client.post('/api/campaigns', json={
        'title': 'Pilot Showcase Workflow',
        'audience': 'Public website demo visitors',
        'goal': 'Interactive product walkthrough',
        'checkpoint': 'none',
        'destinations': ['facebook', 'instagram']
    })
    assert campaign_resp.status_code == 201
    campaign = campaign_resp.json()
    assert campaign['snapshot']['publishing'] == 'simulation'
