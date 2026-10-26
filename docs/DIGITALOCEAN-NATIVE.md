# VTAB website integration without Docker

Deploy this separate marketing workspace at `marketing.vtabsquare.com`. The existing website, Sales Intelligence and Lead Management services remain independent. A protected admin navigation link can point to the marketing address after acceptance. This is a separate login, not single sign-on or an iframe embed. The app prohibits iframe embedding.

## Current status

The repository includes native service/proxy configuration and fail-closed startup validation. These files do not mean the droplet has been deployed. Check actual capacity and port availability on the website server before installation. The suggested 512 MB process limit is a ceiling, not a measured capacity guarantee.

## Server installation

Use the DigitalOcean console or an authorized SSH session. First inspect `free -m`, `df -h /`, `ss -ltn`, `systemctl --failed`, and `nginx -T`. Record existing website health and configuration. Port 4321 must be unused. Do not restart or replace the existing VTAB applications, reuse their databases, or upgrade global Python packages.

Install Python 3.11+, venv support and Git using the Ubuntu package manager if absent. Create a dedicated system account and an isolated release directory:

```bash
sudo useradd --system --home-dir /var/lib/vtab-marketing --shell /usr/sbin/nologin vtab-marketing
sudo install -d -m 0755 /opt/vtab-marketing/releases
sudo git clone https://github.com/vtabsquare/Vtab-ai-agent-marketing.git /opt/vtab-marketing/releases/initial
cd /opt/vtab-marketing/releases/initial
# Record the exact revision with git rev-parse HEAD.
sudo python3 -m venv .venv
sudo .venv/bin/python -m pip install -r requirements.txt
sudo ln -s /opt/vtab-marketing/releases/initial /opt/vtab-marketing/current
sudo install -d -m 0700 /etc/vtab-marketing
sudo install -m 0600 deploy/digitalocean/environment.example /etc/vtab-marketing/environment
```

If an account/path already exists, inspect it first; do not overwrite it. The precompiled React dashboard is included, so no Node build is required on the droplet.

Privately edit `/etc/vtab-marketing/environment`. Choose a unique owner password of at least 16 characters. Generate the encryption key with `.venv/bin/python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'` and the webhook secret with `.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(48))'`. Save values privately; never paste them into GitHub, chat, logs or screenshots. Keep an offline recovery copy of the encryption key. The owner password variable also resets that owner's password on startup; manage it carefully.

```bash
sudo install -m 0644 deploy/digitalocean/vtab-marketing.service /etc/systemd/system/vtab-marketing.service
sudo systemctl daemon-reload
sudo systemctl enable --now vtab-marketing
curl --fail -H 'Host: marketing.vtabsquare.com' http://127.0.0.1:4321/api/health
```

Expect server mode and simulation publishing. Without authentication, `/api/settings` must return 401. The one application process includes its background worker; do not run a second worker or multiple Uvicorn workers against this installation. Jobs continue when browsers are closed. This processes queued workflows and due analytics/community tasks; it does not automatically create recurring campaigns on a fixed calendar. Configure and approve workflows in the dashboard.

## Domain and HTTPS

At the authoritative DNS provider, add an A record for `marketing` to the chosen droplet's verified public IPv4 address. Do not change the main domain's records or nameservers. Check that the hostname is not already in use.

Back up Nginx configuration, then install the separate site:

```bash
sudo install -m 0644 deploy/digitalocean/marketing.nginx.conf /etc/nginx/sites-available/vtab-marketing
sudo ln -s /etc/nginx/sites-available/vtab-marketing /etc/nginx/sites-enabled/vtab-marketing
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d marketing.vtabsquare.com --redirect
```

Certbot must already be installed from Ubuntu or the official supported channel. Complete any certificate subscriber terms yourself if required. Never sign in over HTTP; keep secure cookies enabled. Test `certbot renew --dry-run` after issuance.

## Acceptance and website link

1. Verify HTTPS, dashboard assets, health `mode=server`, and `publishing=simulation`.
2. Verify `/api/settings` rejects unauthenticated access, then verify owner login/logout.
3. Set reviewed VTAB brand facts and scan the company website read-only. Keep social publishing in simulation; leave notification/provider credentials absent until separately configured.
4. Run a simulation workflow through approval and completion; verify persistence after restarting only `vtab-marketing`.
5. Check `systemctl status vtab-marketing`, `journalctl -u vtab-marketing`, resource consumption and the existing website/Lead Management/Sales Intelligence health.
6. Add an **AI Marketing Manager** link to the website's protected admin navigation. A link does not grant shared authentication. Do not publish owner credentials.

Use the in-app online backup for data and retain the environment file/encryption key securely. For updates, take an online backup, deploy a new isolated release, switch the `current` symlink and restart only this service. Retain the previous release and a tested restore path. Configuration rollback alone cannot undo database migrations. Do not copy a live SQLite database without its WAL/online-backup protocol.
