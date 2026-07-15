# Shortink

An open-source URL shortener with a clean web dashboard. Paste a long URL, get a compact short link, and manage everything from a single page.

## Features

- **Shorten URLs** -- paste any URL, get a 5-character base62 short code
- **Click tracking** -- each redirect increments a click counter
- **Edit & delete** -- update destination URLs or custom short codes anytime
- **Copy to clipboard** -- one-click copy of your short URL
- **Search/filter** -- quickly find links by URL, code, or short URL
- **Dark theme** -- responsive UI that works on phone, tablet, and desktop
- **Fast redirects** -- Redis-backed for low-latency URL resolution
- **User authentication** -- register, login, and JWT-based session management

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | React 19, TypeScript, Vite |
| Database | Redis |
| Auth | JWT (HS256), bcrypt |
| Styling | Vanilla CSS (dark theme) |

## Project Structure

```
shortink/
  main.py                     # Entry point
  .env                        # Environment config
  backend/
    source/
      main.py                 # FastAPI app factory
      api/routes/             # API route handlers
      config/                 # Settings, Redis, database
      models/                 # Data models & schemas
      security/               # Auth, hashing, JWT
      utils/                  # Base62, exceptions, messages
    tests/                    # Test suite (pytest)
  frontend/
    src/
      App.tsx                 # Main app component
      api.ts                  # API client
      components/             # UI components
      styles.css              # Dark theme styles
    vite.config.ts            # Dev server & proxy config
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Redis instance (local or cloud)

### Backend

```bash
# Install dependencies
uv sync
# or
pip install -e .

# Configure environment
cp .env.example .env   # then edit with your values

# Run the server
uvicorn main:backend_app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` and proxies API requests to the backend.

### Production Build

```bash
cd frontend
npm run build
npm run preview
```

## Environment Variables

All variables are loaded from a single `.env` file at the project root.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `DEV` | Set to `PROD` to enforce JWT_SECRET |
| `JWT_SECRET` | Yes (PROD) | dev fallback | Secret key for JWT signing |
| `JWT_EXPIRATION_MINUTES` | No | `1440` | Token lifetime in minutes |
| `REDIS_URL` | Conditional | constructed | Full Redis connection URL |
| `REDIS_HOST` | No | `localhost` | Redis host |
| `REDIS_PORT` | No | `6379` | Redis port |
| `PUBLIC_BASE_URL` | No | empty | Public base URL for short links |
| `VITE_API_BASE_URL` | No | empty | Frontend API base (empty = proxy) |

## API Endpoints

### Shortlinks

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/shortlinks` | Create a shortlink |
| `GET` | `/shortlinks` | List all shortlinks |
| `GET` | `/shortlinks/{id}` | Get a shortlink by ID |
| `PUT` | `/shortlinks/{id}` | Update a shortlink |
| `DELETE` | `/shortlinks/{id}` | Delete a shortlink |

### Redirects

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/{short_code}` | Redirect to original URL |
| `GET` | `/s/{short_code}` | Redirect (tiny path) |
| `GET` | `/r/{short_code}` | Redirect (legacy path) |

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and get JWT token |
| `GET` | `/auth/me` | Get current user (requires Bearer token) |

### Auto-generated Docs

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Running Tests

```bash
pytest backend/tests/
```

Tests use FakeRedis and in-process ASGI transport -- no real Redis instance needed.

## License

MIT -- see [LICENSE](LICENSE) for details.
