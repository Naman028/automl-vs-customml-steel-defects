Test suites for this repository.

Frontend (Playwright):

- Tests location: tests/playwright/
- Install and run:
  cd frontend
  npm install
  npm i -D @playwright/test
  npx playwright install
  # From project root:
  npx playwright test tests/playwright

Backend assistant tests (standard library; no extra package required):

- Run from the project root:
  `python -m unittest tests.api.test_assistant_unittest -v`

Backend live API tests (pytest + requests):

- Tests location: tests/api/
- Start backend (example):
  .\scripts\run_backend.ps1
- Run tests (from project root):
  python -m pytest tests/api -q -s

Notes:

- Playwright tests assume the frontend dev server is running at http://localhost:5173
- API tests assume backend is running at http://localhost:8001
- Override with `API_BASE_URL` when needed
- If endpoints or ports differ, update the test URLs accordingly
- Use one backend start command in one terminal only; avoid starting multiple Uvicorn processes on the same port.
