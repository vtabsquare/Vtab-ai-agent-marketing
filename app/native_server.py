"""Fail-closed entrypoint for the native, single-process HTTPS deployment."""
import os
from pathlib import Path


def validate_environment():
    if os.environ.get("MARKETING_MODE") != "server":
        raise RuntimeError("Set MARKETING_MODE=server for the native deployment.")
    password = os.environ.get("MARKETING_ADMIN_PASSWORD", "")
    if len(password) < 16 or password.strip() != password:
        raise RuntimeError("Configure a unique administrator password of at least 16 characters without surrounding whitespace.")
    if not os.environ.get("MARKETING_ADMIN_EMAIL", "").strip():
        raise RuntimeError("Configure MARKETING_ADMIN_EMAIL.")
    from cryptography.fernet import Fernet
    try:
        Fernet(os.environ.get("MARKETING_SECRET_KEY", "").encode())
    except (ValueError, TypeError):
        raise RuntimeError("Configure a valid Fernet MARKETING_SECRET_KEY.") from None
    if len(os.environ.get("MARKETING_WEBHOOK_SECRET", "")) < 32:
        raise RuntimeError("Configure a random webhook secret of at least 32 characters.")
    hosts = os.environ.get("MARKETING_ALLOWED_HOSTS", "").split(",")
    if not hosts or any(not host.strip() or "*" in host for host in hosts):
        raise RuntimeError("Configure explicit MARKETING_ALLOWED_HOSTS without wildcards.")
    if os.environ.get("MARKETING_COOKIE_SECURE", "true").lower() != "true":
        raise RuntimeError("HTTPS deployment requires secure session cookies.")
    data = Path(os.environ.get("MARKETING_DATA_DIR", ""))
    if not data.is_absolute():
        raise RuntimeError("Use an absolute persistent MARKETING_DATA_DIR.")


def create_app():
    validate_environment()
    from .main import create_app as factory
    return factory()
