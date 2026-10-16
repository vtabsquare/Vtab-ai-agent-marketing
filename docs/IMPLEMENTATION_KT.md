# Implementation and developer KT

## Product boundary

This is a dedicated, single-client marketing workspace that can operate with or without a CRM. One installation owns one client's data directory. It is not a shared multi-tenant SaaS billing platform. FastAPI serves the compiled React UI and SQLite durable state. Run one application process against a local persistent volume.

## Three data modes

| Mode | Source of truth | Best fit | Inputs |
| --- | --- | --- | --- |
| Standalone | Built-in workspace | Businesses with no CRM | Website scan, manual catalog/audiences/leads, CSV, forms and internal lead inbox |
| Connected | External system | Clients whose CRM stays authoritative | Registered CRM/connector entities plus campaign operations |
| Hybrid | Per-domain ownership | CRM plus local marketing data | Connector records with website knowledge, catalog, forms, campaigns and memory |

Every workflow stores an immutable capability snapshot. Later settings changes affect new workflows only. `app/capabilities.py` is the source of truth.

## Four channel states

| State | Behavior |
| --- | --- |
| Disabled | No content or action for that channel |
| Content only | Generate/review/export channel copy; never publish |
| Publishing connected | Approve, schedule and publish through a verified account |
| Fully connected | Publishing plus supported metrics and engagement ingestion |

Discord, X and LinkedIn have native text publishing. Instagram, Facebook, email and web export remain content destinations until their adapters are implemented. Never label a channel fully connected unless publishing, metrics and engagement contracts exist.

## Phase-by-phase implementation

1. Stabilization: real publishing contracts, explicit unavailable metrics, deterministic demo analytics, research provenance and schema tracking.
2. Capability foundation: the three modes, four channel states and workflow snapshots.
3. Website intelligence: bounded same-host crawl, sitemap discovery, facts/prices, change detection, provenance and prompt-injection flags.
4. Standalone data: catalog, audiences, leads, CSV mapping/import, deduplication, consent, status, ownership, notes and export.
5. Multi-channel: selected destinations, channel variants, content-only paths and per-platform idempotency.
6. Memory: client, performance, campaign and agent scopes with review and expiry lifecycle.
7. Dynamic workflows: versioned, validated DAG registry and capability-aware availability.
8. Conversion: landing pages, hosted consent forms, UTM generation and metric events.
9. Analytics: funnels, historical context and descriptive controlled experiments.
10. Connectors: canonical entities, ownership, cursors, idempotent sync, outbox and dead letters.
11. Productization: named accounts, five roles, secure sessions, audit, diagnostics, recoverable backup and release gate.

## Architecture and extension points

- `app/main.py`: API composition and security middleware.
- `app/store.py`: schema versions 1–8 and core persistence.
- `app/workflow_registry.py` + `config/workflows.json`: workflow definitions.
- `app/agents.py`, `config/agents.json`, `config/prompts.json`: role, tool, memory and versioned-prompt policy.
- `app/controller.py`: execution, approvals, retries, memory and handoffs.
- `app/website.py`, `standalone.py`, `memory.py`, `conversion.py`, `analytics.py`: domain services.
- `app/connectors.py`: connector SDK and registered types.
- `app/integrations.py`: external publishing and measurement.
- `app/operations.py`: PBKDF2 accounts, sessions, RBAC, metadata-only audit, diagnostics and online backup.
- `frontend/src/ControlCenter.jsx` + `control.css`: modern capability control center.

## Connector contract

Canonical entities are `contact`, `account`, `product`, `segment`, `interaction`, `conversion` and `consent`. A connector declares access mode, capabilities, owned domains and field mapping. Inbound records are idempotent by connector/entity/external ID. Outbound changes enter an approved outbox. Failures belong in dead letters. Connector-owned fields must not be silently overwritten locally.

The generic adapter is a contract and test harness, not completed vendor OAuth. HubSpot and Salesforce are registered product targets; real OAuth refresh, rate limits and production API transport still require implementation and client-account staging.

## Memory and knowledge rules

Only approved memories are injected. Candidate memories need review. Scopes are `client`, `performance`, `agent.<role>` and `campaign.<id>`. Keep sensitivity and expiry. Website items retain URL, retrieval time, hash and approval state. Never convert raw CRM payloads or untrusted website instructions directly into permanent memory.

## Security and recovery

Server mode requires `MARKETING_ADMIN_PASSWORD` with 16+ characters and bootstraps login `admin` as owner. Legacy HTTP Basic remains compatible. Session cookies are HTTP-only, SameSite Strict and secure by default. Roles: owner, admin, editor, analyst and viewer. Trusted host and origin checks remain active.

Audit records contain actor, method, path, status and time—not bodies, keys or lead messages. Credentials use Fernet. `/api/backup` uses SQLite online backup and bundles `marketing.db`, `secret.key` and restore instructions. Protect this archive as confidential client data.

## API groups added

- Capabilities and workflow definitions
- Website scans and knowledge decisions
- Catalog, audiences, leads, imports and exports
- Memory lifecycle
- Landing pages, public forms, UTM and events
- Funnel analytics and experiments
- Connector types, sync, records and outbox
- Login, users, audit, diagnostics and backup

Open `/docs` on a running installation for exact schemas.

## Release gate

Run `python release_check.py`. It validates registries, compiles Python, runs all backend tests, runs frontend tests, rebuilds the UI and verifies a fresh schema-version-8 database. Live CRM/social/provider accounts are intentionally a client-staging check.
