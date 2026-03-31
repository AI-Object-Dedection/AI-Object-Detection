# AI Object Detection

An AI-powered object detection and image analysis application built with FastAPI (backend) and React (frontend).

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A Google Cloud project with OAuth 2.0 credentials (for authentication)
- A Google Gemini API key (for AI analysis)

## Quick Start

### 1. Configure the backend environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and fill in the required values:

```env
# Database – automatically set by Docker Compose, but you can override it here
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/construction_ai

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT
SECRET_KEY=your-strong-secret-key-at-least-32-characters

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Debug mode (set to False in production)
DEBUG=True
```

### 2. Start the backend with Docker Compose

Before starting, export the required database credentials (or add them to a root-level `.env` file):

```bash
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=change_me_strong_password
```

```bash
docker-compose up --build
```

This command starts:
- **PostgreSQL 15** database on port `5432`
- **FastAPI backend** on port `8000`

The backend creates all required database tables automatically on first startup.

### 3. Verify the backend is running

```bash
# Health check
curl http://localhost:8000/health

# API root
curl http://localhost:8000/

# Interactive API docs (only available when DEBUG=True)
open http://localhost:8000/docs
```

### 4. Configure and start the frontend

```bash
cp frontend/.env.example frontend/.env
# Edit frontend/.env and set REACT_APP_GOOGLE_CLIENT_ID

cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`.

## Running in the background

```bash
# Start services in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Development

### Backend only (without Docker)

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment file
cp .env.example .env
# Edit .env with your DATABASE_URL and other settings

# Run the development server
python main.py
```

### Database migrations

```bash
# Inside the backend container
docker-compose exec backend alembic upgrade head
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/api/v1/auth/...` | Authentication (Google OAuth) |
| GET/POST | `/api/v1/photos/...` | Photo upload & management |
| GET | `/api/v1/analytics/...` | Analytics data |
| GET | `/api/v1/search/...` | Search functionality |
| GET | `/api/v1/stats/...` | Statistics |

