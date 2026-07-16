# Statsig Application - Full Stack Prototype

A full-stack application with a Django backend (REST API + Celery + Redis +
Server-Sent Events), and a TypeScript frontend — a legacy Express/vanilla-JS
UI plus a Vite + React + SWR client for live SSE updates.

## Project Structure

```
.
├── backend/                  # Django REST API
│   ├── app/                 # Django project config (settings, urls, celery.py, asgi.py)
│   ├── core/                # Core app: models, views, serializers, Celery tasks
│   ├── certs/                # Self-signed TLS cert/key for local HTTPS (generated, gitignored)
│   ├── Dockerfile           # Backend Docker image
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/, public/         # Legacy Express + vanilla-JS UI (port 9090)
│   ├── client/               # Vite + React + TypeScript + SWR client (port 5173)
│   │   └── src/              # api.ts (fetcher), useSSE.ts (EventSource hook), App.tsx
│   ├── Dockerfile           # Frontend Docker image
│   └── package.json         # Node dependencies (legacy Express app)
├── docker-compose.yml         # Docker Compose configuration
└── .env                      # Environment variables
```

> Local dev uses SQLite by default (no Postgres container needed). Setting
> `DB_ENGINE` (as `docker-compose.yml` does) switches to Postgres — see
> [Database](#database) below.


## Features

- **Django Backend**: RESTful API (DRF) with SQLite (local) / PostgreSQL (Docker)
- **Celery + Redis**: background task queue; `publish_sse_event` task pushes events to SSE
- **Server-Sent Events**: `django-eventstream` + Daphne (ASGI) stream live events to clients
- **TypeScript Frontend**: legacy Express UI (port 9090), plus a Vite + React + SWR client (port 5173) that revalidates data live via `EventSource`
- **Docker Compose**: Full containerization for local development and deployment

## API Endpoints

### Backend (Django)
- `POST /statsig` - Submit JSON data to be stored in the database (DRF router, `trailing_slash=False`)
  ```json
  {
    "data": {"key": "value", "key2": "value2"}
  }
  ```

- `GET /api/hello/` - Simple hello endpoint

- `GET /api/events/?channel=global` - SSE stream (django-eventstream). Requires an ASGI
  server (Daphne) — hangs/blocks under `runserver`/WSGI.

- `POST /trigger-events` - `SSEEventViewSet` (DRF `ModelViewSet`). Persists an `SSEEvent`
  row, then queues the `publish_sse_event` Celery task, which calls
  `django_eventstream.send_event()` and pushes to any client subscribed on `/api/events/`.
  ```json
  {
    "channel": "global",
    "event_type": "message",
    "payload": {"message": "hi"}
  }
  ```

### Frontend (TypeScript)
- `GET http://localhost:9090/` - Legacy Express UI
- `POST /api/submit` - Submit data to backend (legacy UI)
- `GET /api/data` - Get data status (legacy UI)
- `GET http://localhost:5173/` - Vite + React + SWR client; subscribes to `/api/events/`
  and revalidates the `/statsig` SWR key on every message

## Quick Start

### Prerequisites
- Docker
- Docker Compose
- (Optional: Python 3.11+, Node.js 18+ for local development)

### Option 1: Run with Docker Compose (Recommended)

```bash
# Clone and navigate to the project
cd full-stack-tools

# Build and start all services
docker-compose up --build

# Services will be available at:
# Frontend: http://localhost:9090
# Backend API: http://localhost:8000
# Database: localhost:5432
```

To stop the services:
```bash
docker-compose down
```

To stop and remove volumes (clean database):
```bash
docker-compose down -v
```

### Option 2: Local Development Setup

#### Backend Setup

Local dev uses **SQLite by default** — no Postgres container needed. Redis is
still required (Celery broker + SSE backing store).

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Redis (separate terminal) — required for Celery + SSE
docker run -p 6379:6379 redis

# Run migrations (creates backend/db.sqlite3)
python manage.py migrate

# Celery worker (separate terminal)
celery -A app worker -l info

# Start the server via Daphne (ASGI) — NOT `runserver`.
# runserver is sync/WSGI and hangs on the /api/events/ streaming response.
daphne -b 0.0.0.0 -p 8000 app.asgi:application
```

To use Postgres locally instead of SQLite, set `DB_ENGINE` before migrating:
```bash
export DB_ENGINE="django.db.backends.postgresql"
export DB_NAME="statsig_db"
export DB_USER="postgres"
export DB_PASSWORD="postgres"
export DB_HOST="localhost"
python manage.py migrate
```

#### Frontend Setup

**Legacy Express UI** (port 9090, plain form -> `/statsig`):
```bash
cd frontend
npm install
npm run build
npm start
```

**Vite + React + SWR client** (port 5173, live SSE demo):
```bash
cd frontend/client
npm install
npm run dev
# → http://localhost:5173
```
This client opens an `EventSource` on `/api/events/?channel=global`; every
message calls SWR's `mutate()` on the `/statsig` key, so the list re-fetches
live. It points at `http://localhost:8000` by default — set `VITE_API_BASE`
to override (e.g. `https://localhost:8443` when testing with TLS, see
[HTTPS for local dev](#https-for-local-dev) below).

## Usage

1. **Access the Frontend**: Open http://localhost:9090 in your browser (legacy UI), or http://localhost:5173 for the SSE + SWR demo
2. **Submit Data**: Enter "key" and "value" fields and click "Submit to Backend"
3. **Backend Processing**: The data is sent to Django and stored in the database (SQLite locally, PostgreSQL in Docker)
4. **View Response**: The response from the backend is displayed in the UI

## Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DB_NAME=statsig_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Django Configuration
DEBUG=True

# Frontend Configuration
DJANGO_API_URL=http://backend:8000
```

## Database

- **Local dev (`python manage.py runserver`/`daphne` directly):** SQLite by
  default, `backend/db.sqlite3`. No `DB_ENGINE` env var needed.
- **Docker Compose:** Postgres, via `DB_ENGINE=django.db.backends.postgresql`
  set in `docker-compose.yml` for the `backend` and `celery_worker` services.
- To use Postgres locally without Docker, set `DB_ENGINE` (and the other
  `DB_*` vars) yourself before running `migrate` — see
  [Local Development Setup](#option-2-local-development-setup).

## Development Commands

### Docker Compose Commands

```bash
# Build services
docker-compose build

# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Django Commands (in backend container)

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access Django shell
docker-compose exec backend python manage.py shell
```

### Database Commands

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d statsig_db

# List tables
\dt

# Quit
\q
```

## Testing the API

### Quick Start (Fresh Deploy & Test)

```bash
# Clean rebuild and start all services
docker-compose down && docker-compose up --build -d && sleep 15

# Run migrations
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Test the POST endpoint with curl
curl -X POST http://localhost:8000/statsig \
  -H "Content-Type: application/json" \
  -d '{"data": {"key": "feature_flag", "key2": "enabled"}}'
```

### Using curl

```bash
# Submit data to backend
curl -X POST http://localhost:8000/statsig \
  -H "Content-Type: application/json" \
  -d '{"data": {"key": "test_key", "key2": "test_value"}}'

# Hello endpoint
curl http://localhost:8000/api/hello/
```

### Using Python requests

```python
import requests

response = requests.post(
    'http://localhost:8000/statsig',
    json={'data': {'key': 'test_key', 'key2': 'test_value'}}
)
print(response.json())
```

### Testing SSE + Celery

```bash
# Open a stream and leave it connected — this should hang open, not return immediately
curl -N http://127.0.0.1:8000/api/events/?channel=global

# In another terminal, trigger an event — it should appear on the curl above instantly
curl -X POST http://localhost:8000/trigger-events \
  -H "Content-Type: application/json" \
  -d '{"channel": "global", "event_type": "message", "payload": {"message": "hi"}}'
```
If the first `curl` never receives anything, check that you're running
`daphne`, not `manage.py runserver` — SSE needs ASGI.

### HTTPS for local dev

For a self-signed cert to test Daphne over TLS:
```bash
cd backend/certs
./generate-cert.sh          # writes cert.pem + key.pem (gitignored)
cd ..
daphne -e ssl:8443:privateKey=certs/key.pem:certKey=certs/cert.pem -p 8000 app.asgi:application
```
Visit `https://localhost:8443/api/events/?channel=global` once in a browser
first to click through the self-signed cert warning — otherwise `EventSource`
connections silently fail. `curl -k` bypasses the warning from the CLI.

For a trusted-by-the-OS cert (e.g. testing against a real browser without
warnings, or for k8s ingress), use `mkcert` instead:
```bash
mkcert -install                  # generates local CA, installs into OS/browser trust store
mkcert seahorse.local            # issues seahorse.local+1.pem / seahorse.local+1-key.pem
kubectl create secret tls seahorse-tls --cert=seahorse.local+1.pem --key=seahorse.local+1-key.pem
```

## Troubleshooting

### Frontend can't connect to backend
- Ensure backend is running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`
- Verify CORS is enabled in Django settings

### Database connection errors
- Local dev uses SQLite by default — if you see `connection to server at "localhost", port 5432 failed`, you have `DB_ENGINE` set somewhere (env var or shell profile) forcing Postgres. `unset DB_ENGINE` or run Postgres: `docker-compose logs db` / see [Database](#database).
- In Docker: check if PostgreSQL is running: `docker-compose logs db`
- Verify database name and credentials in `.env`
- Run migrations: `docker-compose exec backend python manage.py migrate` (Docker) or `python manage.py migrate` (local)

### SSE not receiving events / `EventSource` hangs
- Confirm you're running `daphne`, not `python manage.py runserver` — SSE requires ASGI.
- Confirm Celery worker is running and logs the task: `celery -A app worker -l info`.
- Confirm Redis is up: `redis-cli ping` → `PONG`.
- If testing over the self-signed cert, open the HTTPS URL in a browser tab once first to accept the certificate — otherwise `EventSource` fails silently.

### `frontend/client` — `npm run dev` fails with "Could not resolve 'vite'"
- `node_modules` is missing or incomplete. Run `rm -rf node_modules package-lock.json && npm install` inside `frontend/client` (not `frontend/`, which is the separate legacy Express app), and check the install output for errors.

### Port already in use
- Change ports in `docker-compose.yml` or `.env`
- Kill process using the port: `lsof -i :9090` then `kill -9 <PID>`

## Project Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | Django 5.0+, Django REST Framework |
| Task Queue | Celery + Redis |
| Realtime | django-eventstream (SSE) + Daphne (ASGI) |
| Database | SQLite (local dev) / PostgreSQL 15 (Docker) |
| Legacy Frontend | Express + TypeScript, HTML5 + CSS3 + Vanilla JS |
| SSE Client | Vite + React + TypeScript + SWR |
| Containerization | Docker + Docker Compose |

## License

MIT

## Next Steps

- Add authentication (JWT tokens)
- Implement data validation and error handling
- Add unit and integration tests
- Deploy to cloud (AWS, GCP, Azure)
- Add database migrations management
- Implement logging and monitoring