# MomentAIc Backend

**The Entrepreneur Operating System** - AI-Native Startup Management Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1.5-purple.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Overview

MomentAIc is an AI-powered platform that helps entrepreneurs build and scale their startups. It combines:

- **Neural Signal Engine** - Real-time startup health monitoring
- **Agent Swarm** - LangGraph-powered AI specialists (Sales, Content, Tech, Finance, etc.)
- **Agent Forge** - Visual workflow automation builder
- **Growth Engine** - CRM + Content Studio
- **Vision Portal** - AI-powered code generation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐│
│  │  Auth   │  │Startups │  │ Signals │  │ Growth  │  │ Agents ││
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └───┬────┘│
│       │            │            │            │           │      │
│  ┌────┴────────────┴────────────┴────────────┴───────────┴────┐│
│  │                    Service Layer                            ││
│  └─────────────────────────────┬───────────────────────────────┘│
│                                │                                 │
│  ┌─────────────────────────────┴───────────────────────────────┐│
│  │                   LangGraph Agents                          ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       ││
│  │  │Supervisor│ │Sales     │ │Content   │ │Tech Lead │       ││
│  │  │          │ │Hunter    │ │Creator   │ │          │       ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ PostgreSQL  │  │    Redis    │  │   Celery    │              │
│  │ + pgvector  │  │             │  │   Workers   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.111 (async) |
| Database | PostgreSQL 16 + pgvector |
| ORM | SQLAlchemy 2.0 (async) |
| AI Orchestration | LangChain + LangGraph |
| LLM Providers | Google Gemini Pro, Claude 3.5 Sonnet |
| Task Queue | Celery + Redis |
| Auth | JWT with refresh tokens |
| Payments | Stripe |
| Container | Docker + Docker Compose |

## 🚦 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+ with pgvector extension
- Redis 7+
- Docker & Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/yourorg/momentaic-backend.git
cd momentaic-backend

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head
```

The API will be available at `http://localhost:8000/api/v1/docs`

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start PostgreSQL and Redis (required)
# Make sure they're running on localhost

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔑 Environment Variables

Required environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/momentaic

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Security
JWT_SECRET_KEY=your-super-secret-key-change-this

# AI Providers (at least one required)
GOOGLE_API_KEY=your-gemini-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key  # Optional

# Stripe (for billing)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

See `.env.example` for all available options.

## 📚 API Documentation

When running locally, visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/signup` | Register new user |
| `POST /api/v1/auth/login` | Login and get tokens |
| `GET /api/v1/startups` | List user's startups |
| `GET /api/v1/signals/{startup_id}` | Get startup health signals |
| `POST /api/v1/agents/chat` | Chat with AI agents |
| `POST /api/v1/forge/workflows` | Create workflow |
| `POST /api/v1/growth/content/generate` | Generate content |

## 🤖 AI Agents

The Agent Swarm includes specialized AI agents:

| Agent | Specialization |
|-------|----------------|
| **Supervisor** | Routes queries to specialists |
| **Sales Hunter** | Lead research & outreach |
| **Content Creator** | Social media & blog content |
| **Tech Lead** | Architecture & code review |
| **Finance CFO** | Financial analysis & fundraising |
| **Growth Hacker** | Growth experiments |
| **Product PM** | Product management |

### Chat with Agents

```bash
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me write a LinkedIn post about our product launch",
    "startup_id": "your-startup-uuid",
    "agent_type": "supervisor"
  }'
```

## 🔧 Agent Forge Workflows

Create automated workflows with a visual DAG builder:

```python
# Example workflow definition
workflow = {
    "name": "Daily Lead Outreach",
    "nodes": [
        {"id": "trigger", "type": "trigger", "label": "Daily 9am"},
        {"id": "fetch", "type": "http", "label": "Fetch new leads"},
        {"id": "research", "type": "ai", "label": "Research leads"},
        {"id": "draft", "type": "ai", "label": "Draft emails"},
        {"id": "approve", "type": "human", "label": "Review & approve"},
        {"id": "send", "type": "notification", "label": "Send emails"}
    ],
    "edges": [
        {"source": "trigger", "target": "fetch"},
        {"source": "fetch", "target": "research"},
        {"source": "research", "target": "draft"},
        {"source": "draft", "target": "approve"},
        {"source": "approve", "target": "send"}
    ],
    "trigger_type": "schedule",
    "trigger_config": {"cron": "0 9 * * *"}
}
```

## 💰 Credit System

| Operation | Credits |
|-----------|---------|
| Signal calculation | 5 |
| Agent chat message | 1 |
| Content generation | 3 |
| Outreach generation | 2 |
| Vision Portal | 20 |
| Workflow run | 10 |

### Tiers

| Tier | Monthly Credits | Price |
|------|-----------------|-------|
| Starter | 50 | Free |
| Growth | 500 | $29/mo |
| God Mode | 5000 | $99/mo |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run async tests
pytest tests/ -v --asyncio-mode=auto
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `APP_ENV=production`
- [ ] Use strong `JWT_SECRET_KEY`
- [ ] Configure HTTPS/SSL
- [ ] Set up proper CORS origins
- [ ] Configure Stripe production keys
- [ ] Set up monitoring (Sentry, Datadog, etc.)
- [ ] Configure log aggregation
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Enable Redis persistence

### Deploy to Production

```bash
# Build production image
docker build -t momentaic:latest .

# Push to registry
docker push your-registry/momentaic:latest

# Deploy with docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📁 Project Structure

```
momentaic-backend/
├── app/
│   ├── agents/          # LangGraph AI agents
│   ├── api/v1/          # API endpoints
│   │   └── endpoints/   # Route handlers
│   ├── core/            # Config, DB, Security
│   ├── middleware/      # Custom middleware
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── tasks/           # Celery tasks
│   ├── utils/           # Helpers
│   └── main.py          # Application entry
├── alembic/             # Database migrations
├── tests/               # Test suite
├── scripts/             # Utility scripts
├── .github/workflows/   # CI/CD
├── docker-compose.yml   # Development setup
├── Dockerfile           # Container definition
└── requirements.txt     # Dependencies
```

## 🔒 Security

- JWT authentication with refresh tokens
- Password hashing with bcrypt
- Rate limiting (tier-based)
- Row-level security for multi-tenancy
- Input validation with Pydantic
- SQL injection prevention via ORM
- CORS protection
- Encrypted token storage

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📞 Support

- Documentation: [docs.momentaic.com](https://docs.momentaic.com)
- Issues: [GitHub Issues](https://github.com/yourorg/momentaic-backend/issues)
- Discord: [Join our community](https://discord.gg/momentaic)

---

Built with ❤️ by the MomentAIc Team
