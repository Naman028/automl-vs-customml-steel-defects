# Frontend Guide

React + Vite UI for:
- single image scan
- batch scan
- model comparison dashboard
- assistant interaction

## Run Frontend Only

From project root:

```powershell
cd frontend
npm install
npm run dev
```

## API Connection

Frontend API modules:
- `frontend/src/app/services/api.ts` (barrel)
- `frontend/src/app/services/api/` (typed modules)

Backend default URL is defined in:
- `frontend/src/app/services/api/constants.ts`

## Notes

- Frontend expects backend on `http://localhost:8001`.
- Use `scripts/run_dev.ps1` from project root to run backend + frontend with one command.
