# Deploying a private client workspace

This release supports a dedicated installation per client. Each installation has its own database, encrypted credentials, domain and administrator password. It is not a shared multi-tenant SaaS service. SQLite uses a bounded connection pool, WAL and a 30-second busy timeout, with short write transactions and separate read connections. Run one application instance on a local persistent disk; do not place its database on a network share or scale replicas against the same SQLite volume.

## Local use

Install Python 3.11 or newer, extract the full project, and run `python deploy.py`. The bundled dashboard needs no Node installation. The first run downloads Python dependencies. Keep the launcher running for background work. Local mode binds to loopback and should not be exposed to the internet.

## Client server with HTTPS

1. Install Docker Engine and Docker Compose on the client server. Point a domain to it and allow inbound ports 80 and 443.
2. Copy `server.env.example` to `.env`. Set the real domain and a unique administrator password of at least 16 characters.
3. Generate `MARKETING_SECRET_KEY` using `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` in an environment with the application dependencies. Generate a separate webhook signing secret of at least 32 random characters.
4. Store these values securely in `.env`; restrict file permissions to the server administrator. Retain an offline recovery copy of the encryption key. Losing it makes saved credentials unreadable.
5. Run `docker compose up -d --build`. Open the HTTPS domain and sign in with username `admin` and the configured password. Caddy obtains and renews the TLS certificate. The backend port is exposed only inside the Docker network.
6. Open Settings, set the brand, configure Gemini, save and test the model connection. Configure social and image providers as needed.

One instance serves one client. The first owner can create named owner, admin, editor, analyst and viewer accounts through the operations API; legacy Basic login remains available for compatibility. This does not provide shared-SaaS tenant isolation, metered billing or SSO. Session and Basic authentication must be used only over HTTPS. Rotate the bootstrap administrator password in `.env`, and manage named accounts separately.

## Publishing and measurement

Simulation is the default and never posts externally. Explicitly choose Live in Settings and one destination before creating a new campaign. Each campaign retains its mode and destination snapshot, and requires approval of its exact copy and creative version. These adapters currently publish text posts; generated visuals remain available in the campaign preview and SVG export.

Discord needs an incoming webhook URL. X needs an OAuth user access token with write permission; app API keys alone are insufficient. LinkedIn needs an access token with posting permission and the author URN for a person or organization. Service permissions, billing, quotas and token expiry remain the client's responsibility.

Each confirmed live publication schedules analytics for 24 hours after confirmation. The wait is stored in SQLite and survives restarts; the task runs when the worker is next available after its due time. X metrics are retrieved from its post lookup endpoint. Impression counts require appropriate access and eligible posts. Discord and the current LinkedIn adapter report metrics as unavailable; they never substitute fake counts. A failed retrieval blocks analytics for review and a deliberate retry.

The publication ledger prevents automatic duplicate submissions after a timeout or restart. If a submission has an unknown outcome, verify the platform account before initiating another campaign; the app deliberately refuses to repeat the uncertain submission.

## Community webhook bridge

For X, a native callback is included at `https://YOUR_DOMAIN/api/webhooks/x`. Save the app's OAuth 2.0 client secret (preferred) or OAuth 1.0 API secret in Social Integrations. Register this URL with X and subscribe to `post.reply.create` through the X Activity API with the required user authorization. The callback answers CRC challenges, verifies native HMAC signatures, matches replies to saved publication receipts, and deduplicates events in the same Community inbox. Legacy Account Activity `tweet_create_events` reply payloads are also accepted. Account Activity is deprecated; use X Activity for new subscriptions. Registration and subscription require account access and are not performed automatically by this app.

`POST /api/webhooks/engagement` accepts a normalized event from a trusted bridge, rather than accepting raw platform callbacks. Configure the platform's official webhook/event subscription separately. The bridge must verify that platform's native signature and translate its event into:

```json
{"event_id":"platform-event-id","campaign_id":"saved-campaign-id","platform":"twitter","post_id":"confirmed-post-id","author":"Customer name","text":"Customer comment"}
```

Send `X-Marketing-Timestamp` as Unix seconds. Send `X-Marketing-Signature` as the hex HMAC-SHA256 of `timestamp + "." + exact_request_body`, signed using `MARKETING_WEBHOOK_SECRET`. Requests older than five minutes, bad signatures, oversized bodies and comments not matching a confirmed publication are rejected. Events are deduplicated by platform and event ID.

The background worker drafts replies and places them in Community for human approval or rejection. Approved replies remain drafts for your team to send. This release does not post community replies automatically. Drafting has three bounded attempts and survives restarts. Discord and LinkedIn require a platform-specific callback bridge and subscription; their native event adapters are not included. The generic listener alone does not create subscriptions.

Service references: [X Activity event payloads](https://docs.x.com/x-api/activity/event-payloads), [X webhook signatures and challenges](https://docs.x.com/x-api/webhooks/introduction), [X post creation](https://docs.x.com/x-api/posts/create-post), [Discord webhooks](https://docs.discord.com/developers/resources/webhook), [LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api), [Hugging Face text to image](https://huggingface.co/docs/inference-providers/tasks/text-to-image).

## Images

Creative Bot writes a campaign-specific visual prompt. Local templates run offline. Hugging Face uses its official InferenceClient with a configurable model and inference provider. FLUX.1-schnell is the default model identifier, subject to current provider availability and account access. Failures appear as task errors rather than blank success images. Pollinations remains an optional alternative. Generation happens once in the worker; previews only render the saved asset.

## Backups and updates

Owners and administrators can call `POST /api/backup`; it uses SQLite's online backup API and returns an archive containing the database, encryption key and restore manifest. Also protect the environment configuration. Backups contain client content and need equivalent access protection. Test restoring to a separate installation before relying on them. Never copy a running database file alone while WAL writes are active.

Before an update, back up the data volume and retain the old image. Rebuild and start the new image, then check health, login, configuration and a simulation campaign. Test upgrades and restore procedures with client data in a staging environment before rollout. Local saved settings are migrated to encrypted values at startup. Existing completed demo campaigns keep their original evidence.
