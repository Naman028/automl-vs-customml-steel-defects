# Verification

Install `requirements/requirements-dev.txt` for fixture tests. The local TFLite runtime
is separate in `requirements/requirements-local.txt`; it is not required by fixture CI.

```powershell
.\.venv\Scripts\python.exe -m pytest -m "not requires_weights and not requires_datasets and not live_api" --cov --cov-report=xml
```

`requires_weights` marks tests that read checkpoints or TFLite exports.
`requires_datasets` marks tests that read locally provisioned experiment manifests
or datasets. CI excludes both categories and the `live_api` marker. HTTP/provider
fixture tests mock predictions and reject external network connections. Internal
loopback socket operations remain available for Windows TestClient support.

After provisioning approved artifacts, run the complete test collection locally.
Set `RUN_ARTIFACT_TESTS=true` to opt in to saved-manifest integration checks, or
`RUN_LIVE_API_TESTS=true` with a backend running to enable the live API smoke test.
`API_BASE_URL` overrides that test's default local backend URL.

Frontend checks:

```bash
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run build
cd frontend
npx playwright install chromium
npm test
```

Playwright starts its own Vite server and supplies a small mocked GC10 response.
The smoke test verifies the home page and navigation into the GC10 experiment;
it requires neither a backend nor model weights.
