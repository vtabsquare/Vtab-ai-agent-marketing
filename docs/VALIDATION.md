# Validation

Current results and limits are in [RELEASE_NOTES.md](RELEASE_NOTES.md). Run `python -m pytest tests -q` from the project directory. Run `node --test frontend/api.test.mjs` and `npm --prefix frontend run build` to check frontend response handling and compile the dashboard. Integration tests use mocked service responses; verify live accounts and server setup in staging.
