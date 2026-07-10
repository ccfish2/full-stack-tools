# Statsig Application - Full Stack Prototype

A complete full-stack application with Django backend, PostgreSQL database, and TypeScript frontend.

## Project Structure

```
.
├── backend/              # Django REST API
│   ├── app/             # Django app configuration
│   ├── core/            # Core app with models and views
│   ├── Dockerfile       # Backend Docker image
│   └── requirements.txt  # Python dependencies
├── frontend/            # TypeScript/Express frontend
│   ├── src/            # TypeScript source code
│   ├── public/         # Static HTML files
│   ├── Dockerfile      # Frontend Docker image
│   └── package.json    # Node dependencies
├── docker-compose.yml   # Docker Compose configuration
└── .env                # Environment variables
```

## Features

- **Django Backend**: RESTful API with PostgreSQL integration
- **TypeScript Frontend**: Express server with modern UI (port 9090)
- **PostgreSQL Database**: Persistent data storage
- **Docker Compose**: Full containerization for local development and deployment

## API Endpoints

### Backend (Django)
- `POST /statsig/application/` - Submit JSON data to be stored in the database
  ```json
  {
    "key": "value",
    "key2": "value2"
  }
  ```
  Response:
  ```json
  {
    "status": "success",
    "id": 1,
    "data": {"key": "value", "key2": "value2"},
    "created_at": "2024-01-01T12:00:00Z"
  }
  ```

- `GET /api/hello/` - Simple hello endpoint

### Frontend (TypeScript)
- `GET http://localhost:9090/` - Main UI
- `POST /api/submit` - Submit data to backend
- `GET /api/data` - Get data status

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
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Note: Local development uses SQLite by default unless you set environment variables
# For PostgreSQL, set these environment variables:
export DB_ENGINE="django.db.backends.postgresql"
export DB_NAME="statsig_db"
export DB_USER="postgres"
export DB_PASSWORD="postgres"
export DB_HOST="localhost"

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Build TypeScript
npm run build

# Start server (runs on port 9090)
npm start
```

## Usage

1. **Access the Frontend**: Open http://localhost:9090 in your browser
2. **Submit Data**: Enter "key" and "value" fields and click "Submit to Backend"
3. **Backend Processing**: The data is sent to Django and stored in PostgreSQL
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
curl -X POST http://localhost:8000/statsig/application/ \
  -H "Content-Type: application/json" \
  -d '{"key": "feature_flag", "key2": "enabled"}'
```

### Using curl

```bash
# Submit data to backend
curl -X POST http://localhost:8000/statsig/application/ \
  -H "Content-Type: application/json" \
  -d '{"key": "test_key", "key2": "test_value"}'

# Hello endpoint
curl http://localhost:8000/api/hello/
```

### Using Python requests

```python
import requests

response = requests.post(
    'http://localhost:8000/statsig/application/',
    json={'key': 'test_key', 'key2': 'test_value'}
)
print(response.json())
```

### Make client stay connect 
```
  curl -N http://127.0.0.1:8000/api/event
```

### Make https for k8s dev and browser
mkcert -install                  # generates local CA, installs into OS/browser trust store
mkcert seahorse.local            # issues seahorse.local+1.pem / seahorse.local+1-key.pem
kubectl create secret tls seahorse-tls --cert=seahorse.local+1.pem --key=seahorse.local+1-key.pem

## Troubleshooting

### Frontend can't connect to backend
- Ensure backend is running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`
- Verify CORS is enabled in Django settings

### Database connection errors
- Check if PostgreSQL is running: `docker-compose logs db`
- Verify database name and credentials in `.env`
- Run migrations: `docker-compose exec backend python manage.py migrate`

### Port already in use
- Change ports in `docker-compose.yml` or `.env`
- Kill process using the port: `lsof -i :9090` then `kill -9 <PID>`

## Project Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | Django 5.2+ |
| Database | PostgreSQL 15 |
| Frontend Server | Express + TypeScript |
| Frontend UI | HTML5 + CSS3 + Vanilla JS |
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
