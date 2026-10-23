# Marketing OS (AI Marketing Manager)
## Master Handover, Technical Architecture & Operational Runbook

**Version:** 2.4.0 (Production Stable)  
**Classification:** Internal Technical Handover  
**Repository:** [https://github.com/vtabsquare/Vtab-ai-agent-marketing.git](https://github.com/vtabsquare/Vtab-ai-agent-marketing.git)  
**Primary Live Deployment:** `https://vtab-ai-agent-marketing-a5ek.onrender.com`  
**Database Cluster:** Supabase PostgreSQL Pooler (AWS Southeast Asia - Singapore)  

---

## Table of Contents
1. [Executive Summary & System Purpose](#1-executive-summary--system-purpose)
2. [System Architecture & Data Flow](#2-system-architecture--data-flow)
3. [The 10 Autonomous Agents Pipeline](#3-the-10-autonomous-agents-pipeline)
4. [Environment Variables & Security Configuration](#4-environment-variables--security-configuration)
5. [Local Development & Engineering Setup](#5-local-development--engineering-setup)
6. [Cloud Production Deployment (Render + Supabase)](#6-cloud-production-deployment-render--supabase)
7. [Meta Graph API & WhatsApp Cloud API Setup](#7-meta-graph-api--whatsapp-cloud-api-setup)
8. [Brand Brain & Website Intelligence Ingestion](#8-brand-brain--website-intelligence-ingestion)
9. [Community Inbox & 2-Way Engagement Engine](#9-community-inbox--2-way-engagement-engine)
10. [Operational Runbooks & Troubleshooting](#10-operational-runbooks--troubleshooting)

---

## 1. Executive Summary & System Purpose

**Marketing OS** is a private, enterprise-grade autonomous marketing department. Traditional marketing teams manually juggle disparate point solutions:
* Copy generation (ChatGPT / Claude)
* Visual generation & formatting (Canva / Midjourney)
* Scheduling & social distribution (Hootsuite / Buffer)
* Direct customer outreach (WhatsApp Web / third-party broadcast tools)
* Inbound comment management (Meta Business Suite inbox)

Marketing OS unifies this entire lifecycle into a single, closed-loop operating system governed by **10 specialized AI agents**. It takes a high-level marketing goal, discovers verified brand context, formulates strategy, synthesizes visual banners and platform-native copy, presents human-in-the-loop approval checkpoints, executes live multi-channel publication, and handles incoming customer inquiries with brand-grounded AI responses.

### Key Business Metrics & Capabilities:
* **Omnichannel Live Publishing:** Official integrations with Meta Graph API (Instagram Feed, Facebook Page Feed), WhatsApp Cloud API (interactive broadcast cards), Discord webhooks, and X/Twitter.
* **Zero-Hallucination Guardrails:** Every piece of copy, pricing claim, or offer is audited by an independent **Brand Guardian** agent against ground-truth database records (**Brand Brain**).
* **2-Way Conversational Conversion:** Full inbound webhook support to capture customer replies and comments in a unified **Community Inbox**, drafting contextual AI replies for 1-click executive sign-off.
* **Tamper-Evident Audit Logging:** Full cryptographic tracking of every agent milestone, approval decision, and live API receipt.

---

## 2. System Architecture & Data Flow

### 2.1 High-Level Component Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend & Control Surface"]
        UI["React 18 Dashboard (Single Page App)"]
        ControlCenter["Capability Control Center"]
        InboxUI["Community & Engagement Hub"]
        AuditUI["Audit Trail & Governance Modal"]
    end

    subgraph APILayer["Backend Application (FastAPI)"]
        Router["FastAPI Application (Port 8000)"]
        AuthMiddleware["Session Auth & AES-256 Vault"]
        Controller["Workflow Controller & Engine"]
        WorkerPool["Background Thread Workers"]
    end

    subgraph AgentLayer["10 Specialized Autonomous Agents"]
        Manager["Marketing Manager (Coordinator)"]
        Research["Research Bot"]
        Strategy["Strategy Bot"]
        Writer["Writer Bot"]
        Creative["Creative Bot (Designer)"]
        Guardian["Brand Guardian"]
        Publisher["Publisher Bot"]
        Analytics["Analytics Bot"]
        Optimizer["Optimizer Bot"]
        CommunityBot["Community Bot"]
    end

    subgraph StorageLayer["Data & Persistence"]
        DB[(Supabase PostgreSQL / SQLite)]
        Vault[(Fernet Encrypted Secrets)]
        CDN["FreeImage CDN / Media Storage"]
    end

    subgraph ExternalAPIs["External Network Integrations"]
        Gemini["Google Gemini (LLM Provider)"]
        HF["HuggingFace FLUX.1 (Image Synthesis)"]
        MetaIG["Meta Graph API (Instagram Feed)"]
        MetaFB["Meta Graph API (Facebook Page)"]
        MetaWA["WhatsApp Cloud API (Messaging)"]
    end

    UI --> Router
    ControlCenter --> Router
    InboxUI --> Router
    AuditUI --> Router

    Router --> AuthMiddleware
    AuthMiddleware --> Controller
    Controller --> WorkerPool
    WorkerPool --> AgentLayer

    AgentLayer <--> Gemini
    Creative <--> HF
    Creative --> CDN

    Publisher --> MetaIG
    Publisher --> MetaFB
    Publisher --> MetaWA

    Router <--> DB
    Router <--> Vault
```

### 2.2 Technology Stack

| Layer | Component | Technology & Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend** | Framework | React 18.3, esbuild / Vite | Responsive dashboard, live agent feeds, control room |
| **Frontend** | Styling | Vanilla CSS modules (`modern.css`, `community.css`) | Zero-dependency high-fidelity UI |
| **Backend** | API Engine | FastAPI 0.142.2, Uvicorn 0.54.0 | High-performance asynchronous REST API |
| **Language** | Runtime | Python 3.12 (slim Docker base) | Core application execution environment |
| **Validation**| Contracts | Pydantic v2 (2.13.5) | Strict schemas for agent contracts and I/O |
| **Database** | Cloud Prod | PostgreSQL (Supabase Pooler) via `psycopg2-binary` | Production transactional state, settings, workflows |
| **Database** | Local Dev | SQLite 3 (WAL mode, busy timeout 30s) | Local zero-dependency execution |
| **Security** | Crypto Vault | Cryptography (Fernet AES-256) | At-rest encryption for Meta tokens, secrets |
| **AI / LLM** | Core Engine | Google Gemini 1.5/2.5 (`google-genai` 1.75.0) | Strategy, copywriting, intent classification |
| **AI / Vision**| Creative Studio | Hugging Face Hub (FLUX.1-schnell / SDXL) | Text-to-image promotional banner synthesis |
| **Social** | Inbound/Out | Meta Graph API v21.0 & WhatsApp Cloud API | Multi-channel publishing and real-time webhook listeners |

---

## 3. The 10 Autonomous Agents Pipeline

The core engine utilizes an asynchronous multi-agent coordination pipeline defined in `app/controller.py` and `app/agents.py`.

```mermaid
sequenceDiagram
    autonumber
    actor User as Workspace Owner
    participant MM as Marketing Manager
    participant RB as Research Bot
    participant SB as Strategy Bot
    participant WB as Writer Bot
    participant CB as Creative Bot (Designer)
    participant BG as Brand Guardian
    participant PB as Publisher Bot
    participant Meta as Meta APIs (IG/FB/WA)

    User->>MM: Submit Campaign Brief (Goal, Audience, Instructions)
    MM->>RB: Assign Fact Extraction & Audience Research
    RB-->>MM: Validated Findings (Grounded in Brand Brain)
    MM->>SB: Assign Omnichannel Strategy & Content Structure
    SB-->>MM: Multi-Platform Blueprint (IG, FB, WhatsApp)
    par Content Generation
        MM->>WB: Draft Platform-Tailored Copy & Hashtags
        MM->>CB: Prompt FLUX Engine & Generate Visual Creative
    end
    WB-->>MM: Instagram Captions, FB Body, WhatsApp Cards
    CB-->>MM: Rendered Promotional Graphic Banner
    MM->>BG: Submit Combined Copy + Graphic for Brand Audit
    BG-->>MM: Sign-off (Zero Hallucination Verified)
    MM->>User: Request Human-in-the-Loop Approval Checkpoint
    User->>MM: Executive Approval Signed
    MM->>PB: Authorized Dispatch Command
    par Live Execution
        PB->>Meta: Post Photo & Caption to Instagram Feed
        PB->>Meta: Post Creative & Copy to Facebook Page
        PB->>Meta: Broadcast Interactive Card to WhatsApp
    end
    Meta-->>PB: Return Live Post IDs, Message IDs & Permalinks
    PB-->>User: Publication Confirmed with Live Receipts
```

### 3.1 Agent Specification Matrix

| Agent Role | File Definition | Primary Function | Failure Handling & Guardrails |
| :--- | :--- | :--- | :--- |
| **1. Marketing Manager** | `app/controller.py` | Orchestrates pipeline, tracks milestone handoffs, enforces review gates. | Blocks execution if prerequisite agent outputs fail schema validation. |
| **2. Research Bot** | `app/agents.py` | Gathers context, extracts audience pain points, retrieves brand facts. | Auto-fallbacks to verified Brand Intelligence if search engines are rate-limited. |
| **3. Strategy Bot** | `config/agents.json` | Divides campaign goals into distinct channel angles (visual, social, direct). | Schema ensures required distribution channels match active settings. |
| **4. Writer Bot** | `config/agents.json` | Drafts channel-native copy: emojis & hashtags for IG, narrative for FB, CTAs for WhatsApp. | Enforces length constraints and tone guidelines from Brand Brain. |
| **5. Creative Bot** | `app/integrations.py` | Engineers detailed prompts and synthesizes visual banners via Hugging Face FLUX. | Falls back to SVG vector brand card templates if HF inference fails. |
| **6. Brand Guardian** | `app/controller.py` | Cross-checks copy and offers against `brand.facts` and `brand.price`. | Flags and halts workflow if non-existent discounts or dates are detected. |
| **7. Publisher Bot** | `app/integrations.py` | Uploads media to CDN, creates Meta media containers, executes live publishing. | Non-repeatable ledger prevents accidental duplicate live submissions. |
| **8. Analytics Bot** | `app/analytics.py` | Enters 24-hour wait (`SCHEDULED_WAIT`) and queries live Meta impression/like metrics. | Captures only verified platform-reported metrics; never generates synthetic counts. |
| **9. Optimizer Bot** | `app/controller.py` | Analyzes performance differences to formulate A/B test hypotheses. | Feeds successful findings into persistent workspace memories. |
| **10. Community Bot**| `app/community.py` | Processes inbound webhook events, detects sentiment, drafts context-aware replies. | Strictly limits response knowledge to approved Brand Brain records. |

---

## 4. Environment Variables & Security Configuration

Marketing OS utilizes layered credential security. Sensitive credentials (API tokens, app secrets) are **never stored in plain text**; they are encrypted at rest using an AES-256 Fernet vault (`app/credentials.py`).

### 4.1 System Environment Variables Reference

| Variable Name | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `PORT` | Optional | `8000` | Port on which the HTTP server listens (assigned by Render in cloud). |
| `DATABASE_URL` | Cloud | None | PostgreSQL connection string. If omitted, falls back to local SQLite. |
| `MARKETING_DATA_DIR` | Optional | `./data` | Local directory for storing local database, logs, and `secret.key`. |
| `MARKETING_SECRET_KEY` | **Critical** | Auto-generated | 32-byte url-safe base64 string for Fernet database encryption. |
| `MARKETING_ADMIN_PASSWORD`| Yes | None | Master bootstrap password for initial workspace owner login. |
| `MARKETING_ALLOWED_HOSTS` | Optional | `*` | Comma-delimited list of host headers permitted by TrustedHostMiddleware. |
| `MARKETING_WEBHOOK_SECRET`| Optional | None | Secret key (≥32 chars) used to verify inbound webhook HMAC signatures. |
| `GEMINI_API_KEY` | Optional | None | Google Gemini API key. Can also be configured dynamically in Settings. |
| `GEMINI_MODEL` | Optional | `gemini-3.5-flash-lite` | Default Gemini model identifier for agent reasoning. |

### 4.2 Dynamic Database Settings (`settings` row in database)

Stored as an encrypted JSON blob in the database:
* `social_keys.facebook_page_id`: Numeric ID of the Facebook Page (e.g. `1371928256002877`).
* `social_keys.facebook_page_token`: Page Access Token for Facebook & Instagram posting.
* `social_keys.instagram_account_id`: Instagram Business Account ID (`17841422864583641`).
* `social_keys.whatsapp_phone_number_id`: WhatsApp Business Phone Number ID (`1315032858369417`).
* `social_keys.whatsapp_token`: WhatsApp Cloud API Access Token.
* `social_keys.whatsapp_recipient`: Test phone number for direct promotional delivery.
* `social_keys.hf_token`: Hugging Face User Access Token for FLUX image synthesis.

---

## 5. Local Development & Engineering Setup

The application is fully runnable locally on Windows, macOS, and Linux without external cloud dependencies.

### 5.1 Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/vtabsquare/Vtab-ai-agent-marketing.git
cd Vtab-ai-agent-marketing

# 2. Create and activate a Python 3.12 virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# 3. Install production dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Generate local secret key (if running fresh)
python -c "from cryptography.fernet import Fernet; print('MARKETING_SECRET_KEY=' + Fernet.generate_key().decode())"
```

### 5.2 Launching the Local Application

```bash
# Start the FastAPI + Uvicorn server on port 8000
python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```
Open your browser to: **`http://127.0.0.1:8000`**
* **Default Username:** `vitabsquare@gmail.com`
* **Default Password:** `vitabsquare` (or configured admin password)

### 5.3 Executing Verification Tests

Marketing OS maintains an extensive automated test suite covering all agent handoffs, webhook processors, encryption vaults, and live publishing adapters:

```bash
pytest tests/ -v
# Verified: 103 passed in ~15s
```

---

## 6. Cloud Production Deployment (Render + Supabase)

### 6.1 Render Web Service Configuration

The live application is hosted as a Dockerized Web Service on Render:
* **Service Name:** `vtab-ai-agent-marketing`
* **Region:** Oregon (USA) or Singapore
* **Branch:** `main`
* **Environment:** `Docker`
* **Health Check Path:** `/api/health`
* **Auto-Deploy:** Enabled (triggers build on `git push origin main`)

### 6.2 Supabase PostgreSQL Database Setup

The cloud instance utilizes Supabase for persistent multi-user storage:
* **Connection String:**
  ```text
  postgresql://postgres.akvxbcudjgtxuhapqqhi:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres?sslmode=require
  ```
* **Database Tables:**
  - `settings`: Holds encrypted brand settings, publishing keys, and active modes.
  - `campaigns`: Full history of workflows, agent conversations, artifacts, and receipts.
  - `engagement`: Inbound comments, WhatsApp messages, sentiment tags, and reply drafts.
  - `audit`: Immutable, append-only security and operational audit trail.

---

## 7. Meta Graph API & WhatsApp Cloud API Setup

### 7.1 Meta Developer App Topology
* **Meta App ID:** `1678178457042396` (`Vtabsquare Bot`)
* **Facebook Page:** `Vtab Square` (ID: `1371928256002877`)
* **Instagram Business Account:** `@aivtabsquare` (ID: `17841422864583641`)
* **WhatsApp Cloud Business ID:** Phone Number ID `1315032858369417`

### 7.2 Permanent Token Generation (Avoid 1-Hour Expirations)

> [!IMPORTANT]
> Developer tokens from Graph API Explorer expire after **1 hour** (`OAuthException 190`). For long-term production, use **System User Tokens** which **Never Expire**.

#### Method 1: System User (Never-Expiring Token — Enterprise Production)
1. Open [Meta Business Suite System Users](https://business.facebook.com/settings/system-users).
2. Click **Add** → Name: `Marketing OS Bot` → Role: `Admin`.
3. Click **Assign Assets** → Assign the **Vtab Square** Page and WhatsApp Account with Full Control.
4. Click **Generate New Token**:
   - Expiration: **Never**
   - Scopes: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `whatsapp_business_messaging`, `whatsapp_business_management`, `instagram_basic`, `instagram_content_publish`.
5. Copy this token into your app Settings. It will run indefinitely without maintenance.

#### Method 2: Extended Token (60-Day Long-Lived Token)
1. In [Graph API Explorer](https://developers.facebook.com/tools/explorer/?app_id=1678178457042396), generate a Page token.
2. Open the [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/).
3. Paste the token and click **Extend Access Token** at the bottom.
4. Meta converts the 1-hour token into a **60-Day Token**.

### 7.3 Webhook Subscriptions Configuration

Meta sends incoming customer comments and WhatsApp messages to our registered webhook endpoints:

| Product | Callback URL | Verify Token | Subscribed Field |
| :--- | :--- | :---: | :---: |
| **WhatsApp Business** | `https://vtab-ai-agent-marketing-a5ek.onrender.com/api/webhooks/whatsapp` | `vtabsquare` | `messages` |
| **Facebook Page** | `https://vtab-ai-agent-marketing-a5ek.onrender.com/api/webhooks/facebook` | `vtabsquare` | `feed` |

---

## 8. Brand Brain & Website Intelligence Ingestion

To guarantee that the autonomous agents never hallucinate discounts, false policies, or outdated dates, all copy is tethered to the **Brand Brain**:

### 8.1 The Brand Knowledge Model
Defined in `app/contracts.py`:
* `brand.name`: Company or brand entity name.
* `brand.product`: Verified list of offerings and products.
* `brand.price`: Exact price points, currency, and active promotional discounts.
* `brand.tone`: Core communication style and target persona resonance.
* `brand.facts`: Hard factual statements (e.g. branch locations, dates, certifications).

### 8.2 Website Intelligence Scanning
* In the **Control Center**, enter the client's public website URL (e.g. `https://www.sshyderabadbiryani.com`) and click **"Scan website"**.
* The crawler analyzes navigation hierarchies and value propositions, transforming raw text into structured **Discovered Facts**.
* Once approved by the workspace owner, these facts automatically become ground-truth data for all future workflows.

---

## 9. Community Inbox & 2-Way Engagement Engine

Most marketing platforms only publish outward; Marketing OS closes the loop by handling customer conversations:

### 9.1 Inbound Event Processing Pipeline

```mermaid
flowchart LR
    Customer["Customer on Meta / WhatsApp"] -->|Post comment or message| MetaWebhook["Meta Webhook Event"]
    MetaWebhook -->|HTTP POST| WebhookEndpoint["FastAPI /api/webhooks/*"]
    WebhookEndpoint --> Deduplication["Deduplication & Event Store"]
    Deduplication --> Sentiment["AI Sentiment & Intent Classifier"]
    Sentiment --> BrandBrain["Brand Brain Grounding"]
    BrandBrain --> AIDraft["AI Synthesizes Contextual Reply"]
    AIDraft --> CommunityInbox["Community Inbox (Awaiting Review)"]
    CommunityInbox -->|Human Clicks Approve & Send| Dispatch["Meta Graph API Reply Dispatch"]
```

### 9.2 Direct Polling Sync (`sync_social_comments`)
In addition to webhooks, the system includes an active polling engine (`Community.sync_social_comments`). Every 45 seconds (or upon clicking **"Sync Social Comments"**), the engine queries Meta Graph API (`/{post_id}/comments`) directly. This allows comments to appear on `localhost` without needing public webhook tunnels!

---

## 10. Operational Runbooks & Troubleshooting

### 10.1 Issue: Meta Tokens Expired (`OAuthException Code 190`)
* **Symptom:** Publisher Bot fails with `Error validating access token: Session has expired`.
* **Root Cause:** Developer token expired after 60 minutes.
* **Fix:** Generate a new token using the [Graph API Explorer](https://developers.facebook.com/tools/explorer/) (or generate a permanent System User token as described in Section 7.2) and update Settings.

### 10.2 Issue: Webhook Not Delivering Messages
* **Symptom:** Customers send messages on WhatsApp or comment on Facebook, but they don't appear in Community Inbox.
* **Root Cause:** Meta Webhook Callback URL is pointing to a decommissioned or typo URL (e.g. missing the `-a5ek` suffix).
* **Fix:** Verify in Meta Developer Portal that the Callback URL matches your exact live server:
  `https://vtab-ai-agent-marketing-a5ek.onrender.com/api/webhooks/whatsapp`
  Verify Token: `vtabsquare`.

### 10.3 Issue: Research Bot Fails with "Cited a source not returned"
* **Symptom:** Research Bot enters "Needs attention".
* **Root Cause:** DuckDuckGo live search was blocked by cloud IP rate limits.
* **Fix:** Fixed in v2.4.0 (`app/agents.py`). The Research Bot now automatically falls back to approved Brand Brain records when external search engines are throttled.

### 10.4 System Health & Database Backup Runbook
* **Health Check Endpoint:** `GET /api/health` → Returns `{"status":"ok","mode":"server","publishing":"live"}`.
* **Manual Database Backup:** Workspace administrators can trigger an online snapshot by calling `POST /api/backup`, which packages all settings, campaigns, and decryption manifests into a secure downloadable archive.

---
*End of Master Handover Documentation. For inquiries or escalation, contact the workspace administrator at vitabsquare@gmail.com.*
