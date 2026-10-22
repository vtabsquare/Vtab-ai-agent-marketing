import os
from starlette.testclient import TestClient
from app.main import create_app


def test_login_flow_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setenv('MARKETING_MODE', 'server')
    monkeypatch.setenv('MARKETING_ADMIN_EMAIL', 'vitabsquare@gmail.com')
    monkeypatch.setenv('MARKETING_ADMIN_PASSWORD', 'Vtab@123')
    monkeypatch.setenv('MARKETING_COOKIE_SECURE', 'false')

    app = create_app(tmp_path, start_worker=False)
    client = TestClient(app)

    # 1. Unauthenticated requests to protected API should return 401
    resp = client.get('/api/settings')
    assert resp.status_code == 401

    resp = client.get('/api/auth/me')
    assert resp.status_code == 401

    # 2. Public health endpoint should work
    resp = client.get('/api/health')
    assert resp.status_code == 200

    # 3. Invalid credentials should fail
    resp = client.post('/api/auth/login', json={'email': 'vitabsquare@gmail.com', 'password': 'wrong-password'})
    assert resp.status_code == 401

    # 4. Valid login with vitabsquare@gmail.com and Vtab@123 should succeed
    resp = client.post('/api/auth/login', json={'email': 'vitabsquare@gmail.com', 'password': 'Vtab@123'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['authenticated'] is True
    assert data['user']['email'] == 'vitabsquare@gmail.com'
    assert data['user']['role'] == 'owner'
    assert 'marketing_session' in client.cookies

    # 5. With cookie active, /api/auth/me and /api/settings should succeed
    resp = client.get('/api/auth/me')
    assert resp.status_code == 200
    assert resp.json()['user']['email'] == 'vitabsquare@gmail.com'

    resp = client.get('/api/settings')
    assert resp.status_code == 200

    # 6. Logout invalidates the session
    resp = client.post('/api/auth/logout')
    assert resp.status_code == 200
    assert resp.json()['signed_out'] is True

    # 7. Post-logout requests are 401 again
    resp = client.get('/api/settings')
    assert resp.status_code == 401
