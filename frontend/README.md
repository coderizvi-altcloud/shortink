# Shortink Frontend

React + Vite dashboard for the Shortink URL shortener API.

## Features

- Create shortlinks from a long URL
- List all shortlinks with click counts
- Copy short URLs to the clipboard
- Edit destination URL or custom short code
- Delete shortlinks
- Live API health indicator

## Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

### Hosted backend

The app is wired to:

`https://shortink-10c51a1f.fastapicloud.dev`

- **Local dev** (`npm run dev`): Vite proxies `/shortlinks` and `/health` to that host (no CORS issues).
- **Production build**: set `VITE_API_BASE_URL` in the project-root `.env` to the hosted API URL.

Redeploy the backend with the CORS middleware in `backend/source/main.py` so direct browser calls work outside the Vite proxy.

## Environment

There is a **single** env file for the whole project: `shortink/.env` (repo root).

Vite is configured with `envDir` pointing at that root — do **not** add `frontend/.env` or other env files.

```bash
# In shortink/.env

# Production / direct API calls
VITE_API_BASE_URL=https://shortink-10c51a1f.fastapicloud.dev

# Local dev (use Vite proxy) — leave empty
VITE_API_BASE_URL=
```

Restart `npm run dev` after changing env vars.

## Build

```bash
npm run build
npm run preview
```
