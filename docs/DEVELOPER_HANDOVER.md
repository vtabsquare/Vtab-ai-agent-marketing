# Developer handover

FastAPI serves the bundled React dashboard and API. Four backend workers dispatch campaign tasks and Community drafts. SQLite uses a bounded connection pool, short write transactions, persistent leases and generation checks to discard superseded results.

`app/workflow.py` defines task dependencies and states. Writer and Creative Bot run independently after strategy. Brand Guardian and manager decisions gate human approval. `app/controller.py` reserves model budgets, records handoffs, controls revisions and requires exact-version approval before publishing.

`app/tools.py` implements price safeguards, content hashing, local SVG rendering and publication deduplication. `app/integrations.py` generates images once and uses actual social endpoints. Assets are saved with results and included in the approval hash. Preview GET requests never call providers. Uncertain live submissions cannot be automatically repeated.

Live publication places Analytics in SCHEDULED_WAIT for 24 hours. Due work is claimed from persisted timestamps. Only platform-reported metrics are measured; unavailable values remain null.

`app/community.py` maintains a separate persisted queue, bounded draft retries and human decisions. `app/x_webhooks.py` verifies native X signatures and CRC challenges and matches replies to saved publication receipts. `app/main.py` also exposes a signed normalized listener for trusted external bridges. Approved reply drafts are not posted automatically.

`app/credentials.py` encrypts credentials using Fernet. Server mode requires a strong administrator password, configured trusted hosts/origins and HTTP Basic authentication behind HTTPS. Webhook routes use signature authentication.

`frontend/src/api.js` handles unexpected response types. `styles.css` supplies component layout; `modern.css` supplies the modern visual system. `Bots.jsx` uses local distinct vector icons without remote fonts or image dependencies.

Use DEPLOYMENT.md and RELEASE_NOTES.md for current operation and limits. Earlier workflow blueprints are historical references.
