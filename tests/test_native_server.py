from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from app.native_server import validate_environment


@pytest.fixture
def native_env(monkeypatch, tmp_path):
    values = {
        'MARKETING_MODE': 'server',
        'MARKETING_ADMIN_EMAIL': 'owner@example.invalid',
        'MARKETING_ADMIN_PASSWORD': 'isolated-test-password-only',
        'MARKETING_SECRET_KEY': Fernet.generate_key().decode(),
        'MARKETING_WEBHOOK_SECRET': 'fixture-only-webhook-secret-32-characters',
        'MARKETING_ALLOWED_HOSTS': 'marketing.example.invalid,127.0.0.1',
        'MARKETING_COOKIE_SECURE': 'true',
        'MARKETING_DATA_DIR': str(tmp_path),
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return values


def test_explicit_native_configuration_is_accepted(native_env):
    validate_environment()


@pytest.mark.parametrize(('key', 'value'), [
    ('MARKETING_MODE', 'local'),
    ('MARKETING_ADMIN_PASSWORD', ''),
    ('MARKETING_ADMIN_PASSWORD', 'Vtab@123'),
    ('MARKETING_ADMIN_PASSWORD', ' trailing-whitespace-password '),
    ('MARKETING_ADMIN_EMAIL', ''),
    ('MARKETING_SECRET_KEY', ''),
    ('MARKETING_SECRET_KEY', 'invalid-key'),
    ('MARKETING_WEBHOOK_SECRET', 'short'),
    ('MARKETING_ALLOWED_HOSTS', '*'),
    ('MARKETING_ALLOWED_HOSTS', 'marketing.example.invalid,'),
    ('MARKETING_COOKIE_SECURE', 'false'),
    ('MARKETING_DATA_DIR', './data'),
])
def test_insecure_native_configuration_is_rejected(native_env, monkeypatch, key, value):
    monkeypatch.setenv(key, value)
    with pytest.raises(RuntimeError):
        validate_environment()


def test_systemd_uses_single_loopback_process_and_private_storage():
    service = (Path(__file__).resolve().parents[1] / 'deploy/digitalocean/vtab-marketing.service').read_text()
    assert '--host 127.0.0.1 --port 4321 --workers 1' in service
    assert 'UMask=0077' in service
    assert 'ReadWritePaths=/var/lib/vtab-marketing' in service
    assert 'app.native_server:create_app' in service
