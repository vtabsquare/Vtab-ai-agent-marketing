# AI Marketing Manager update

This release addresses the supplied issue document, modernizes the interface and adds private client-server deployment facilities. Original Downloads files were not modified. The distributed project excludes the supplied database, credentials, virtual environment and scratch scripts; existing installations should back up and retain their own data before upgrading.

| Requirement | Shipped behavior | Limits |
| --- | --- | --- |
| Graceful server errors | Handles JSON, plain text, HTML and malformed responses; sanitized backend errors | Connection loss retains the last displayed state |
| Database contention | Bounded connection pool, WAL, 30-second busy timeout, short writes and separate reads | One instance on local persistent disk |
| Semantic brand safety | Brand Guardian compares meaning against approved facts; review and manager veto restored; bounded revisions | Gemini required for semantic reasoning; offline demo deterministic. Factual price checks retained |
| Social settings | Masked secure fields, encrypted persistence, explicit live/simulation selection | X user token required; one destination per workflow |
| Live publishing | Discord, X and LinkedIn use actual endpoints and receipts; durable duplicate-submission protection | Text posts only; no image upload adapters |
| Delayed analytics | SCHEDULED_WAIT persisted until 24 hours after confirmation, with restart recovery | Runs when server available after due time. X permissions govern counts; Discord/LinkedIn metrics unavailable |
| Engagement | Durable signed webhook inbox, deduplication, bounded drafting, human approval/rejection; native X signatures and CRC | X subscription must be configured. Discord/LinkedIn need an external bridge. Approved replies sent manually |
| Creative direction | Campaign-specific agent prompt; generic photography suffix removed; saved assets generated once | Local templates remain vector art; photographs require an image provider |
| Hugging Face / FLUX | Official InferenceClient, configurable model/provider, encrypted token, FLUX.1-schnell default identifier | Provider availability, access and billing depend on account |
| Modern UI | Light canvas, violet navigation, distinct vector agent icons, responsive cards, team conversation, map and Community | Desktop/mobile browser checks completed |
| Client servers | Non-root Docker image, Compose, HTTPS proxy, administrator login, persistent data, encrypted secrets and backup guide | Dedicated client installation with one administrator; shared SaaS and multi-user roles are future work |

## Verification

54 backend tests passed. Coverage includes independent execution, concurrent writes, exact-version approval, bounded revisions/retries, credential secrecy, durable scheduling, publication deduplication, signed engagement ingestion, native X callback verification, platform request contracts and Hugging Face request contracts.

Four frontend API tests passed for plain-text server errors, HTML proxy errors, malformed JSON and structured success. Production React build completed. A local browser verified dashboard, campaign creation, approval display, conversation, workflow map, Settings, Community navigation and a 390-pixel mobile layout with no page errors or horizontal overflow. Screenshots were inspected and mobile navigation refined.

External services were tested with mocked transport. No live posts or billable generation were requested. Docker configuration is supplied, but container build and client-server deployment were not verified because Docker is not installed here. Validate account permissions and deployment in client staging before production rollout.
