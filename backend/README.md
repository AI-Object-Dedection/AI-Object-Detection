# AI-Powered Construction Site Monitoring System - Backend

Clean architecture FastAPI backend for construction site photo management and AI-powered analysis.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/      # API route handlers
│   │   │   ├── auth.py     # Authentication endpoints
│   │   │   ├── projects.py # Project management
│   │   │   ├── photos.py   # Photo upload/management
│   │   │   ├── search.py   # Semantic search
│   │   │   └── analytics.py # Analytics & stats
│   │   └── router.py       # API router aggregation
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration management
│   │   ├── database.py     # Database connection
│   │   ├── security.py     # JWT & password handling
│   │   └── dependencies.py # FastAPI dependencies
│   ├── models/             # SQLAlchemy models
│   │   ├── user.py
│   │   ├── project.py
│   │   └── image.py
│   ├── schemas/            # Pydantic schemas
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── image.py
│   │   ├── search.py
│   │   └── analytics.py
│   ├── services/           # Business logic
│   │   ├── ai_service.py      # Gemini AI integration
│   │   ├── embedding_service.py # Text embeddings
│   │   ├── search_service.py  # Semantic search
│   │   └── file_service.py    # File handling
│   └── main.py             # Application entry point
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ with pgvector extension
- Google Gemini API key

### Installation

1. **Clone and navigate to backend**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup PostgreSQL with pgvector**
```sql
CREATE DATABASE construction_ai;
\c construction_ai
CREATE EXTENSION vector;
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

6. **Run migrations**
```bash
alembic upgrade head
```

7. **Start server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Projects
- `POST /api/projects` - Create project
- `GET /api/projects` - List user's projects
- `GET /api/projects/{id}` - Get project details
- `PATCH /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `POST /api/projects/{id}/members` - Add team member

### Photos
- `POST /api/photos/upload` - Upload photos
- `GET /api/photos` - List photos
- `GET /api/photos/{id}` - Get photo details
- `DELETE /api/photos/{id}` - Delete photo

### Search
- `POST /api/search` - Semantic search with natural language

### Analytics
- `GET /api/analytics/stats` - Overall statistics
- `GET /api/analytics/distribution` - Category distribution
- `GET /api/analytics/timeline` - Upload timeline
- `GET /api/analytics` - Complete analytics data

## 🧠 AI Pipeline

### Image Processing Flow

1. **Upload** → Photo uploaded to project
2. **Storage** → File saved with thumbnail generation
3. **AI Analysis** → Gemini generates description + category
4. **Embedding** → Text converted to vector embedding
5. **Indexing** → Vector stored in pgvector for search

### Semantic Search

Uses sentence-transformers with cosine similarity:
- Query → Embedding → Vector search → Ranked results
- Supports natural language: *"concrete work with safety equipment"*

## 🗄️ Database Schema

### Core Tables
- **users** - User accounts and authentication
- **projects** - Construction projects
- **project_members** - Project access control
- **images** - Photo metadata
- **image_descriptions** - AI-generated descriptions
- **image_embeddings** - Vector embeddings for search

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- Project-level authorization
- File upload validation
- SQL injection protection via ORM

## 🛠️ Configuration

Key settings in `.env`:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/construction_ai
SECRET_KEY=your-secret-key-min-32-chars
GEMINI_API_KEY=your-gemini-api-key
CORS_ORIGINS=http://localhost:3000
UPLOAD_DIR=uploads
```

## 📊 Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy 2.0
- **AI**: Google Gemini, sentence-transformers
- **Auth**: JWT, bcrypt
- **File handling**: Pillow

## 🧪 Development

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📦 Production Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Use strong `SECRET_KEY`
3. Configure PostgreSQL with connection pooling
4. Use HTTPS for all endpoints
5. Set up background task queue (Celery/Redis) for AI processing
6. Enable CORS only for production domains

## 🎯 Key Features

✅ JWT authentication & authorization  
✅ Multi-project support with access control  
✅ AI-powered image description (Gemini)  
✅ Semantic search with vector embeddings  
✅ Real-time analytics & statistics  
✅ Automatic thumbnail generation  
✅ Category-based filtering  
✅ Date range analytics  

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Construction AI Monitoring System - Thesis Project 2025
