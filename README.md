# Statsig Application - Full Stack Prototype

A full-stack prototype: a Django backend (REST API + Server-Sent Events + Celery background tasks) with a React/TypeScript client built with Vite, PostgreSQL/Redis in Docker Compose.

## Project Structure

```
.
├── backend/                  # Django backend
│   ├── app/                  # Project config (settings, urls, asgi, celery)     
│   ├── core/                 # Main app: models, views, serializers, Celery tasks
          api
            v1/               # Django v1 contract
            v2/               # Django v2 contract
          migrations
│   ├── templates/            # index.html (mounts the React client via django-vite)
│   ├── static/dist/          # Built client assets (generated, served by Django)
│   ├── entrypoint.sh         # Migrates DB, seeds a superuser, starts Daphne (ASGI)
│   └── requirements.txt      # Python dependencies
        Dockerfile
        manage.py
├── frontend/
│   ├── client/                # React + Vite + TypeScript SSE client (active frontend)
│   │   └── src/
                api
                  client.tsx  # http mechanism
                  v1/          # Django API contract
                    featureFlags.ts
                    events.ts
                  v2/         # Django v2 API contract
                    featureFalgs.ts
                    events.ts

                features      # Feature behavior UI
                    featureFlags
                      components
                      hooks
                      types.ts
                      index.ts
                
                    evetns
                      components
                      hooks
                      types.ts
                           
│   └──     App.tsx           # Compose UI. For example: knows featurefalgs --> client.tsx ---> api/v1
            main.tsx 
            useSSE.ts         # SSE lifecycle + SWR invalidation
        vite.config.ts
        tsconfig.json
        package.json      
├── docker-compose.yml         # db, backend, redis, celery_worker services
└── .env                       # Environment variables
```

## Features

- **Django Backend**: REST API (Django REST Framework) served over ASGI via Daphne
- **Server-Sent Events**: Real-time updates pushed to clients via `django-eventstream`, backed by Redis
- **Celery Background Tasks**: SSE events are persisted then published asynchronously by a Celery worker; a separate `django-tasks` (DB-backed) queue handles email jobs
- **React + Vite Client**: TypeScript/React SSE client, integrated into Django via `django-vite` — Django serves the app shell and injects the built (or, in dev, HMR-proxied) client assets
- **PostgreSQL Database**: Used in Docker; local (non-Docker) development falls back to SQLite unless `DB_ENGINE` is set
- **Docker Compose**: Containerized backend, database, Redis, and Celery worker for local development

> Note: `frontend/` also contains a legacy Express/TypeScript server (`frontend/src/server.ts`). It's not part of the current architecture — its service is commented out in `docker-compose.yml` — and is kept around from an earlier iteration of the project.

## API Endpoints

All routes are defined in `backend/app/urls.py`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Renders the app shell (`index.html`), which mounts the React client |
| `GET` | `/api/hello/` | Simple health-check endpoint |
| `GET`, `POST` | `/api/statsigfeatureflag` | CRUD for `StatsigApplication` records (feature flag metadata per product/environment), via a DRF `ModelViewSet` |
| `GET`, `POST` | `/api/trigger-events` | Persists an `SSEEvent` row, then queues a Celery task to publish it over SSE. Body: `{"channel": "global", "event_type": "message", "payload": {...}}` |
| `GET` | `/api/events/?channel=global` | SSE stream (`django-eventstream`). Any client with an open `EventSource` on this URL receives events published via `/api/trigger-events` |
| `POST` | `/api/publishmsg/` | Queues an email notification task on the `django-tasks` DB-backed queue |
| `/admin/` | Django admin |
| `/api_auth/` | DRF browsable-API login |
| `/__reload__/` | `django-browser-reload` (dev only) |

### Example: trigger an SSE event

```bash
curl -X POST http://localhost:8000/api/trigger-events \
  -H "Content-Type: application/json" \
  -d '{"channel": "global", "event_type": "message", "payload": {"hello": "world"}}'
```

Any client subscribed to `GET /api/events/?channel=global` will receive it once the Celery worker processes the task.

### Example: create a feature flag record

```bash
curl -X POST http://localhost:8000/api/statsigfeatureflag \
  -H "Content-Type: application/json" \
  -d '{"product": "checkout", "environment": "stage"}'
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional, for local dev without Docker: Python 3.12+, Node.js 18+, Redis)

### Option 1: Run with Docker Compose (Recommended)

```bash
# Clone and navigate to the project
cd full-stack-tools

# Build and start backend, database, redis, and the celery worker
docker-compose up --build

# Services will be available at:
# App / Backend API: http://localhost:8000
# Database: localhost:5432
# Redis: localhost:6379
```

The backend container's entrypoint automatically runs migrations and creates a default superuser (`admin` / `admin123`) so you can log into `/admin/` right away.

> The frontend service in `docker-compose.yml` is currently commented out. When running via Docker with `DEBUG=True`, Django (via `django-vite`) proxies to a Vite dev server instead — see the frontend setup below to run it alongside `docker-compose up`.

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

```bash
cd backend

# Create virtual environment (Python 3.12+)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Local development uses SQLite by default unless you set DB_ENGINE.
# For PostgreSQL, set these environment variables instead:
export DB_ENGINE="django.db.backends.postgresql"
export DB_NAME="statsig_db"
export DB_USER="postgres"
export DB_PASSWORD="postgres"
export DB_HOST="localhost"

# Run migrations
python manage.py migrate

# Start server (runserver won't stream SSE responses correctly — see note below)
python manage.py runserver
```

Redis is required for both Celery and SSE storage:

```bash
brew install redis        # or your platform's equivalent
brew services start redis # or: redis-server
```

Run the Celery worker in a separate terminal:

```bash
cd backend
celery -A app worker -l info
```

> `manage.py runserver` is WSGI/sync and will hang on the streaming `/api/events/` response. In Docker, the backend runs under Daphne (ASGI) instead — for local SSE testing, run `daphne -b 0.0.0.0 -p 8000 app.asgi:application` rather than `runserver`.

#### Frontend Setup (React + Vite client)

```bash
cd frontend/client
npm install
npm run dev   # starts the Vite dev server on http://localhost:5173
```

With `DEBUG=True` on the backend, Django's `django-vite` integration proxies to this dev server automatically when you load `http://localhost:8000/`.

To build static assets for production (output goes to `backend/static/dist`, matching `DJANGO_VITE` in `settings.py`):

```bash
cd frontend/client
npm run build
```

## Usage

1. **Access the app**: Open <http://localhost:8000> in your browser (Django serves the app shell; in dev it proxies to the Vite client)
2. **Trigger an SSE event**: `POST /api/v1/trigger-events` — the client's `useSSE` hook, connected via `EventSource`, receives it in real time
3. **Manage feature flag records**: use `/api/v1/statsigfeatureflag` or the Django admin at `/admin/`

## Environment Variables

Create a `.env` file in the project root:

```
# Database Configuration
DB_NAME=statsig_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Django Configuration
DEBUG=True
ALLOWED_HOSTS=*
```

`REDIS_HOST` defaults to `redis` in Docker (set via `docker-compose.yml`) and `localhost` otherwise.

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

# View logs for a specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker

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

# Run tests
docker-compose exec backend python manage.py test
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

## API
┌──────────────────────────┬──────────────────────────────┐
│ Code                     │ URL                          │
├──────────────────────────┼──────────────────────────────┤
│ API_BASE                 │ /api                         │
│ fetcher("/events/")      │ /api/v1/events/                 │
│ fetcher("/statsig...")   │ /api/v1/statsigfeatureflag      │
│ fetcher("/trigger...")   │ /api/v1/trigger-events           │
│ SSE                      │ /api/v1/events/?channel=global   │
└──────────────────────────┴──────────────────────────────┘

## Testing the API

```bash
# Clean rebuild and start all services
docker-compose down && docker-compose up --build -d && sleep 15

# Hello endpoint
curl http://localhost:8000/api/v1/hello/

# Create a feature flag record
curl -X POST http://localhost:8000/api/v1/statsigfeatureflag \
  -H "Content-Type: application/json" \
  -d '{"product": "checkout", "environment": "stage"}'

# Trigger an SSE event
curl -X POST http://localhost:8000/api/v1/trigger-events \
  -H "Content-Type: application/json" \
  -d '{"channel": "global", "event_type": "message", "payload": {"hello": "world"}}'
```

### Using Python requests

```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/statsigfeatureflag',
    json={'product': 'checkout', 'environment': 'stage'}
)
print(response.json())
```

## Troubleshooting

### Client can't connect to backend / SSE doesn't update

- Ensure the backend is running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`
- Ensure `redis` and `celery_worker` are both up — SSE events are published by the Celery worker, not the web process
- Verify CORS is enabled in Django settings (`CORS_ALLOW_ALL_ORIGINS`)

### Database connection errors

- Check if PostgreSQL is running: `docker-compose logs db`
- Verify database name and credentials in `.env`
- Run migrations: `docker-compose exec backend python manage.py migrate`

### Port already in use

- Change ports in `docker-compose.yml` or `.env`
- Kill the process using the port: `lsof -i :8000` then `kill -9 <PID>`

## Project Tech Stack

| Component | Technology |
| --- | --- |
| Backend API | Django 6.0.1, Django REST Framework |
| ASGI Server | Daphne |
| Real-time | django-eventstream (SSE) over Redis |
| Background Tasks | Celery + Redis (SSE publishing), django-tasks-db (email queue) |
| Database | PostgreSQL 15 (Docker) / SQLite (local dev default) |
| Frontend Client | React 18 + TypeScript + Vite, integrated via django-vite |
| Containerization | Docker + Docker Compose |

## License

MIT

## Next Steps

- Add unit/integration tests for the SSE and Celery flows