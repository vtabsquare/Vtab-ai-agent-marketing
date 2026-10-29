"""Workspace accounts, sessions, audit history, diagnostics and recoverable backups."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
import uuid
import zipfile
from pathlib import Path

from .store import Conflict, Missing


ROLES = {'owner', 'admin', 'editor', 'analyst', 'viewer'}
ROLE_DESCRIPTIONS = {
    'owner': 'Full workspace control, including accounts, settings, audit and backups.',
    'admin': 'Manage configuration and day-to-day operations, but not owner accounts.',
    'editor': 'Create, review and operate marketing workflows and business records.',
    'analyst': 'Review campaigns, leads, experiments and performance without changing configuration.',
    'viewer': 'Read-only access to workspace information.',
}


def _password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310_000)
    return f'pbkdf2_sha256$310000${salt.hex()}${digest.hex()}'


def _verify(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, expected = encoded.split('$', 3)
        if algorithm != 'pbkdf2_sha256': return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(rounds)).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


class OperationsService:
    SESSION_TTL = 12 * 60 * 60

    def __init__(self, store):
        self.store = store

    @staticmethod
    def public_user(item):
        return {key: item[key] for key in ('id', 'email', 'name', 'role', 'is_pilot', 'active', 'created_at', 'updated_at', 'last_login_at') if key in item}

    def bootstrap_owner(self, password: str, email: str = 'vitabsquare@gmail.com', name: str = 'Vtab Square Owner'):
        email = (os.environ.get('MARKETING_ADMIN_EMAIL') or email).strip().lower()
        now = time.time()
        with self.store.transaction() as db:
            row = db.execute('SELECT id, password_hash, payload FROM users WHERE lower(email)=lower(?)', (email,)).fetchone()
            if row:
                if password and not _verify(password, row[1]):
                    item = json.loads(row[2])
                    item['updated_at'] = now
                    db.execute('UPDATE users SET password_hash=?, updated_at=?, payload=? WHERE id=?',
                               (_password_hash(password), now, json.dumps(item), row[0]))
                return
            # If an old dummy 'admin' account exists without logins, update it to the specified email
            old_admin = db.execute("SELECT id, payload FROM users WHERE lower(email)='admin'").fetchone()
            if old_admin:
                item = {'id': old_admin[0], 'email': email, 'name': name, 'role': 'owner',
                        'active': True, 'created_at': now, 'updated_at': now, 'last_login_at': None}
                db.execute('UPDATE users SET email=?, password_hash=?, updated_at=?, payload=? WHERE id=?',
                           (email, _password_hash(password), now, json.dumps(item), old_admin[0]))
                return
            item = {'id': uuid.uuid4().hex, 'email': email, 'name': name, 'role': 'owner',
                'active': True, 'created_at': now, 'updated_at': now, 'last_login_at': None}
            db.execute('INSERT INTO users(id,email,role,active,password_hash,created_at,updated_at,payload) VALUES(?,?,?,?,?,?,?,?)',
                       (item['id'], item['email'], item['role'], 1, _password_hash(password), now, now, json.dumps(item)))

    def authenticate(self, email: str, password: str):
        with self.store.transaction() as db:
            row = db.execute('SELECT * FROM users WHERE lower(email)=lower(?)', (email,)).fetchone()
            if not row and email.lower() == 'admin':
                row = db.execute("SELECT * FROM users WHERE role='owner' AND active=1 LIMIT 1").fetchone()
            if not row or not row['active'] or not _verify(password, row['password_hash']): return None
            item = json.loads(row['payload']); item['last_login_at'] = time.time(); item['updated_at'] = item['last_login_at']
            db.execute('UPDATE users SET updated_at=?,payload=? WHERE id=?', (item['updated_at'], json.dumps(item), item['id']))
            token = secrets.token_urlsafe(48); token_hash = hashlib.sha256(token.encode()).hexdigest()
            db.execute('INSERT INTO sessions(id,user_id,token_hash,created_at,expires_at) VALUES(?,?,?,?,?)',
                       (uuid.uuid4().hex, item['id'], token_hash, time.time(), time.time() + self.SESSION_TTL))
        return self.public_user(item), token

    def get_or_create_pilot_session(self, email: str = 'demo@vtabsquare.com', name: str = 'Vtab Pilot Guest'):
        email = email.lower()
        now = time.time()
        with self.store.transaction() as db:
            row = db.execute('SELECT id, payload FROM users WHERE lower(email)=lower(?)', (email,)).fetchone()
            if row:
                user_id = row[0]
                item = json.loads(row[1])
                item['last_login_at'] = now
                item['updated_at'] = now
                item['is_pilot'] = True
                db.execute('UPDATE users SET updated_at=?, payload=? WHERE id=?', (now, json.dumps(item), user_id))
            else:
                user_id = 'usr_pilot_demo_vtab'
                item = {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'role': 'editor',
                    'is_pilot': True,
                    'active': True,
                    'created_at': now,
                    'updated_at': now,
                    'last_login_at': now
                }
                dummy_hash = _password_hash(secrets.token_urlsafe(32))
                db.execute(
                    'INSERT INTO users(id,email,role,active,password_hash,created_at,updated_at,payload) VALUES(?,?,?,?,?,?,?,?)',
                    (user_id, email, 'editor', 1, dummy_hash, now, now, json.dumps(item))
                )
            token = secrets.token_urlsafe(48)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            db.execute(
                'INSERT INTO sessions(id,user_id,token_hash,created_at,expires_at) VALUES(?,?,?,?,?)',
                (uuid.uuid4().hex, user_id, token_hash, now, now + 7 * 24 * 3600)
            )
        return self.public_user(item), token

    def session_user(self, token: str):
        if not token: return None
        token_hash = hashlib.sha256(token.encode()).hexdigest(); now = time.time()
        with self.store.reading() as db:
            row = db.execute('SELECT u.payload FROM sessions s JOIN users u ON u.id=s.user_id '
                             'WHERE s.token_hash=? AND s.expires_at>? AND u.active=1', (token_hash, now)).fetchone()
        return self.public_user(json.loads(row[0])) if row else None

    def logout(self, token: str):
        if not token: return
        with self.store.transaction() as db:
            db.execute('DELETE FROM sessions WHERE token_hash=?', (hashlib.sha256(token.encode()).hexdigest(),))

    def users(self):
        with self.store.reading() as db: rows = db.execute('SELECT payload FROM users ORDER BY created_at').fetchall()
        return [self.public_user(json.loads(row[0])) for row in rows]

    def create_user(self, payload, actor):
        if payload['role'] not in ROLES: raise Conflict('Unknown workspace role.')
        if actor['role'] != 'owner' and payload['role'] in {'owner', 'admin'}: raise Conflict('Only an owner can create an owner or administrator.')
        now = time.time(); item = {'id': uuid.uuid4().hex, 'email': payload['email'].lower(), 'name': payload['name'],
            'role': payload['role'], 'active': True, 'created_at': now, 'updated_at': now, 'last_login_at': None}
        try:
            with self.store.transaction() as db:
                db.execute('INSERT INTO users(id,email,role,active,password_hash,created_at,updated_at,payload) VALUES(?,?,?,?,?,?,?,?)',
                           (item['id'], item['email'], item['role'], 1, _password_hash(payload['password']), now, now, json.dumps(item)))
        except sqlite3.IntegrityError: raise Conflict('An account with this email already exists.') from None
        return self.public_user(item)

    def update_user(self, user_id, payload, actor):
        with self.store.transaction() as db:
            row = db.execute('SELECT payload FROM users WHERE id=?', (user_id,)).fetchone()
            if not row: raise Missing('Workspace user not found.')
            item = json.loads(row[0])
            if item['role'] == 'owner' and actor['role'] != 'owner': raise Conflict('Only an owner can change an owner account.')
            if payload.get('role') == 'owner' and actor['role'] != 'owner': raise Conflict('Only an owner can assign ownership.')
            if payload.get('active') is False and item['id'] == actor['id']: raise Conflict('You cannot deactivate your own account.')
            for field in ('name', 'role', 'active'):
                if payload.get(field) is not None: item[field] = payload[field]
            if item['role'] not in ROLES: raise Conflict('Unknown workspace role.')
            item['updated_at'] = time.time()
            db.execute('UPDATE users SET role=?,active=?,updated_at=?,payload=? WHERE id=?',
                       (item['role'], int(item['active']), item['updated_at'], json.dumps(item), user_id))
            if not item['active']: db.execute('DELETE FROM sessions WHERE user_id=?', (user_id,))
        return self.public_user(item)

    def audit(self, actor, request, status):
        if request.method in {'GET', 'HEAD', 'OPTIONS'}: return
        entry = {'id': uuid.uuid4().hex, 'at': time.time(), 'actor_id': actor.get('id', 'anonymous'),
                 'actor': actor.get('email', 'anonymous'), 'role': actor.get('role', 'none'),
                 'method': request.method, 'path': request.url.path, 'status': status}
        with self.store.transaction() as db:
            db.execute('INSERT INTO audit_events(id,occurred_at,actor_id,path,status,payload) VALUES(?,?,?,?,?,?)',
                       (entry['id'], entry['at'], entry['actor_id'], entry['path'], status, json.dumps(entry)))

    def audit_events(self, limit=200):
        with self.store.reading() as db:
            rows = db.execute('SELECT payload FROM audit_events ORDER BY occurred_at DESC LIMIT ?', (max(1, min(limit, 1000)),)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def diagnostics(self):
        with self.store.reading() as db:
            integrity = db.execute('PRAGMA quick_check').fetchone()[0]
            migrations = [row[0] for row in db.execute('SELECT version FROM schema_migrations ORDER BY version').fetchall()]
            tables = {name: db.execute(f'SELECT count(*) FROM {name}').fetchone()[0] for name in
                      ('campaigns', 'leads', 'memories', 'knowledge_items', 'experiments', 'connector_dead_letters')}
        return {'status': 'ok' if integrity == 'ok' else 'attention', 'database_integrity': integrity,
                'schema_versions': migrations, 'records': tables, 'data_directory': str(self.store.folder),
                'configuration': {'mode': self.store.settings().get('data_mode'), 'provider': self.store.settings().get('provider')}}

    def backup(self):
        folder = self.store.folder / 'backups'; folder.mkdir(exist_ok=True)
        stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime()); db_copy = folder / f'marketing-{stamp}.db'
        archive = folder / f'marketing-backup-{stamp}.zip'
        source = self.store.connect(); target = sqlite3.connect(db_copy)
        try: source.backup(target)
        finally: target.close(); source.close()
        manifest = {'created_at': time.time(), 'schema': 8, 'contains': ['marketing.db', 'secret.key'],
                    'restore': 'Stop the application, extract both files into the configured data directory, then restart.'}
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
            bundle.write(db_copy, 'marketing.db')
            key = self.store.folder / 'secret.key'
            if key.exists(): bundle.write(key, 'secret.key')
            bundle.writestr('manifest.json', json.dumps(manifest, indent=2))
        db_copy.unlink(missing_ok=True)
        return archive
