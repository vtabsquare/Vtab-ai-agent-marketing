# AI Marketing Manager

A private adaptive marketing workspace that runs in Standalone, Connected or Hybrid mode. It combines website intelligence, optional CRM connectors, scoped agent memory, multi-channel campaigns, lead capture, analytics, human approvals and a modern capability control center.

## Start locally

Install Python 3.11 or newer, extract the complete project and run `python deploy.py`. On Windows, try `py -3 deploy.py` if Python is unavailable. Use `python deploy.py --port 8001` if the default port is busy.

The launcher downloads Python dependencies on first use and opens http://127.0.0.1:8000. Keep it running for background work. The React dashboard is already compiled; Node is needed only to edit its source.

## Use the workspace

1. Open Settings and enter approved brand facts. Offline demo needs no provider credentials.
2. For real AI output, configure Gemini, save and test its connection.
3. Choose an image provider. Local vector templates work offline; Hugging Face and Pollinations use Creative Bot's campaign-specific prompt.
4. Create a workflow. Follow the team conversation and workflow map, answer requested input, and review the exact content version before approving publication.
5. Simulation is the default. For live posting, select Live and one destination in Settings before creating a new workflow. Discord, X and LinkedIn currently publish text posts.
6. Live analytics waits 24 hours after publication. Accessible X metrics are measured; unavailable values remain empty. Demo fixtures are clearly labeled.
7. Community presents signed incoming comments and human reply approvals. Native X callbacks are supported; other platforms use the documented bridge.

## Deploy to DigitalOcean without Docker

Use the dedicated [native DigitalOcean deployment guide](docs/DIGITALOCEAN-NATIVE.md) for `marketing.vtabsquare.com`, with Nginx, systemd, private persistent storage and validated server-mode startup. The service includes the application worker; one process handles queued jobs. Deployment files are prepared, but installation, DNS, HTTPS and live acceptance must be completed on your server.

## Deploy to Render

Deploy this application directly to [Render](https://render.com) using the included `render.yaml` blueprint or manual setup:

### Option A: Blueprint (Recommended - 1 Click)
1. In your [Render Dashboard](https://dashboard.render.com), click **New +** → **Blueprint**.
2. Connect this repository (`https://github.com/vtabsquare/Vtab-ai-agent-marketing.git`).
3. Render reads `render.yaml` automatically and configures your web service.
4. Click **Apply**.

### Option B: Manual Web Service
1. In Render Dashboard, click **New +** → **Web Service**.
2. Connect your repository: `https://github.com/vtabsquare/Vtab-ai-agent-marketing.git`.
3. Configure the service settings:
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:create_app --factory --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variables**:
   - `PYTHON_VERSION`: `3.12.3`
   - `MARKETING_MODE`: `local`
   - `MARKETING_ALLOWED_HOSTS`: `*`
   - `MARKETING_DATA_DIR`: `./data`
5. Click **Create Web Service**.

## Client server deployment

Docker, Compose, HTTPS proxy, named accounts with five roles, encrypted credentials, audit history, online backup and persistent storage are included. Use one isolated installation per client. Follow [DEPLOYMENT.md](docs/DEPLOYMENT.md) for operations, [IMPLEMENTATION_KT.md](docs/IMPLEMENTATION_KT.md) for architecture and modes, and [IMPLEMENTATION_RELEASE.md](docs/IMPLEMENTATION_RELEASE.md) for current validation.

This is a dedicated-client product foundation, not shared SaaS. SSO, tenant isolation, billing, image upload adapters and automatic community reply posting remain future work. Native Discord and LinkedIn comment bridges require a trusted external integration. Account-backed CRM and social operation must be verified in each client's staging environment.

## Development

Install `requirements-dev.txt`, then run `python release_check.py` for the complete release gate. Rebuild the dashboard after changing its source. Run one application process against SQLite; do not scale replicas against its data volume.
