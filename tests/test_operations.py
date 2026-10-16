import io
import zipfile

from fastapi.testclient import TestClient

from app.main import create_app


def server_client(tmp_path, monkeypatch):
    monkeypatch.setenv('MARKETING_MODE', 'server')
    monkeypatch.setenv('MARKETING_ADMIN_PASSWORD', 'a-strong-client-password')
    monkeypatch.setenv('MARKETING_COOKIE_SECURE', 'false')
    return TestClient(create_app(tmp_path, start_worker=False))


def test_session_login_users_roles_and_audit(tmp_path, monkeypatch):
    with server_client(tmp_path, monkeypatch) as client:
        assert client.get('/api/auth/me').status_code == 401
        login = client.post('/api/auth/login', json={'email':'admin','password':'a-strong-client-password'})
        assert login.status_code == 200 and login.json()['user']['role'] == 'owner'
        created = client.post('/api/users', json={'email':'editor@example.com','name':'Campaign editor',
            'role':'editor','password':'editor-password-123'})
        assert created.status_code == 201
        assert 'password' not in created.text and len(client.get('/api/users').json()) == 2
        audit = client.get('/api/audit').json()
        assert any(item['path'] == '/api/users' and item['status'] == 201 for item in audit)

        client.post('/api/auth/logout')
        assert client.get('/api/settings').status_code == 401
        assert client.post('/api/auth/login', json={'email':'editor@example.com','password':'editor-password-123'}).status_code == 200
        assert client.get('/api/settings').status_code == 200
        assert client.put('/api/settings', json={}).status_code == 403
        assert client.get('/api/users').status_code == 403


def test_diagnostics_and_recoverable_backup(tmp_path, monkeypatch):
    with server_client(tmp_path, monkeypatch) as client:
        client.post('/api/auth/login', json={'email':'admin','password':'a-strong-client-password'})
        diagnostics = client.get('/api/diagnostics')
        assert diagnostics.status_code == 200
        assert diagnostics.json()['database_integrity'] == 'ok'
        assert 8 in diagnostics.json()['schema_versions']
        backup = client.post('/api/backup')
        assert backup.status_code == 200 and backup.headers['content-type'] == 'application/zip'
        with zipfile.ZipFile(io.BytesIO(backup.content)) as bundle:
            assert {'marketing.db','secret.key','manifest.json'} <= set(bundle.namelist())


def test_analyst_is_read_only(tmp_path, monkeypatch):
    brief={'title':'Read only check','audience':'Owners','goal':'Awareness','instructions':'','checkpoint':'none'}
    with server_client(tmp_path, monkeypatch) as client:
        client.post('/api/auth/login', json={'email':'admin','password':'a-strong-client-password'})
        assert client.post('/api/users', json={'email':'analyst@example.com','name':'Analyst','role':'analyst',
            'password':'analyst-password-123'}).status_code == 201
        client.post('/api/auth/logout')
        assert client.post('/api/auth/login', json={'email':'analyst@example.com','password':'analyst-password-123'}).status_code == 200
        assert client.get('/api/campaigns').status_code == 200
        assert client.post('/api/campaigns', json=brief).status_code == 403
