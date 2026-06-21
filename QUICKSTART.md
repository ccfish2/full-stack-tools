# Quick Start Guide

Get the entire prototype running in minutes with Docker Compose!

## 1. Prerequisites

Make sure you have installed:
- Docker (https://www.docker.com/products/docker-desktop)
- Docker Compose (comes with Docker Desktop)

## 2. Clone and Setup

```bash
cd full-stack-tools
```

## 3. Start Everything with Docker Compose

### Option A: Automated Start (Recommended)

```bash
chmod +x start.sh
./start.sh
```

This script will:
- Check Docker installation
- Build all Docker images
- Start all services (Django, PostgreSQL, TypeScript frontend)
- Wait for services to be ready
- Display access URLs

### Option B: Manual Start

```bash
# Build and start services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

## 4. Access the Application

Once services are running, open your browser:

- **Frontend UI**: http://localhost:9090
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/admin/

## 5. Use the Application

1. Go to http://localhost:9090
2. Enter a key and value
3. Click "Submit to Backend"
4. The data is stored in PostgreSQL and response is displayed

## 6. Test the Backend API Directly

```bash
# Submit data
curl -X POST http://localhost:8000/statsig/application/ \
  -H "Content-Type: application/json" \
  -d '{"key": "feature_flag", "key2": "enabled"}'

# Test hello endpoint
curl http://localhost:8000/api/hello/
```

## 7. Stop Services

```bash
# Stop running containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

## 8. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

## 9. Database Access

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d statsig_db

# List tables
\dt

# Query statsig data
SELECT * FROM core_statsigapplication;

# Exit
\q
```

## 10. Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Restart everything
docker-compose down -v
docker-compose up --build
```

### Port already in use
```bash
# Kill process on port 9090
lsof -i :9090
kill -9 <PID>

# Change port in docker-compose.yml if needed
```

### Frontend can't reach backend
- Check if backend is running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`
- Verify backend is listening: `curl http://localhost:8000/api/hello/`

## 11. Project Structure

```
.
├── backend/              # Django REST API
│   ├── app/             # Django configuration
│   ├── core/            # App with models and views
│   ├── Dockerfile       # Docker image
│   ├── entrypoint.sh    # Startup script
│   └── requirements.txt  # Dependencies
├── frontend/            # TypeScript/Express frontend
│   ├── src/            # Server code
│   ├── public/         # Static HTML
│   ├── Dockerfile      # Docker image
│   └── package.json    # Dependencies
├── docker-compose.yml   # Service orchestration
├── .env                # Configuration
├── start.sh            # Startup script
└── README.md           # Full documentation
```

## 12. Next Steps

- Check [README.md](README.md) for detailed documentation
- Explore the admin panel at http://localhost:8000/admin/
- Customize the frontend in `frontend/public/index.html`
- Add more endpoints in `backend/core/views.py`
- Deploy to cloud using the Docker images

## 13. Development Mode

To work on the code locally without Docker:

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run build
npm start
```

## 14. Support

- Django docs: https://docs.djangoproject.com/
- PostgreSQL docs: https://www.postgresql.org/docs/
- Express docs: https://expressjs.com/
- Docker docs: https://docs.docker.com/

---

**Happy coding! 🚀**
