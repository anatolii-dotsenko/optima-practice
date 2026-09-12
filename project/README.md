# Coffee Shop Online Ordering System (Вебсистема онлайн-замовлень у кав'ярні)

An artisanal coffee shop online ordering platform built as part of the practice report project. The system provides customer registration and login, online menu browsing, cart management, and pre-orders.

---

## Technology Stack

- **Backend:** Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, PyJWT, bcrypt.
- **Frontend:** HTML5, Modern Vanilla ES Modules, Custom Design Tokens & Responsive CSS.
- **Database:** PostgreSQL 16 (production container) / SQLite (in-memory for isolated testing).
- **Containerization:** Podman / Podman Compose (rootless, non-root user, multi-stage builds).
- **CI / Quality:** pytest, ruff, GitHub Actions.

---

## Architectural Principles

The codebase strictly enforces the **Three-Tier Architecture** and layer rules defined in `report-spec/spec/engineering-plan.yaml`:
1. `api -> services -> repositories -> database; never skip a layer`
2. `services must not import the web framework` (FastAPI / Starlette)
3. `repositories are the only place that constructs queries` (SQLAlchemy queries only in `repositories/`)
4. `schemas (DTOs) never leak ORM models to the client`

---

## Project Structure

```text
project/
├── backend/
│   ├── app/
│   │   ├── api/             # HTTP layer only (routing, status codes, DTOs)
│   │   ├── core/            # Config, security (bcrypt/JWT), logging, DB session
│   │   ├── models/          # SQLAlchemy ORM models (User)
│   │   ├── repositories/    # Database queries (UserRepository)
│   │   ├── schemas/         # Pydantic DTOs (RegisterRequest, TokenResponse, etc.)
│   │   ├── services/        # Pure domain business logic (AuthService)
│   │   └── main.py          # FastAPI application entry point
│   ├── tests/               # pytest test suite (unit and integration)
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/             # Isolated API client (no hardcoded URLs)
│   │   ├── components/      # Reusable UI components (Navbar, etc.)
│   │   ├── pages/           # Pages with explicit states (login, register, profile)
│   │   ├── styles/          # Design tokens & CSS
│   │   └── main.js          # Client SPA router
│   ├── index.html
│   └── package.json
├── deploy/
│   ├── Containerfile.backend    # Multi-stage, non-root user, pinned python:3.12.7
│   ├── Containerfile.frontend   # Unprivileged nginx static runtime
│   └── podman-compose.yml       # Orchestration with named volume pgdata
├── docs/
│   ├── adr/                 # Architecture Decision Records (ADR-0001 to ADR-0005)
│   └── api/                 # OpenAPI 3.1 schema & Markdown API reference
├── report-spec/             # Specifications and report generation tooling
├── AGENTS.md                # Normalized engineering specification instructions
└── .env.example             # Environment variable template
```

---

## Quick Start Guide

### Prerequisites
- Python 3.9+ (or Podman / Podman Compose)
- Git

### 1. Local Development (Backend)

```bash
# Navigate to the backend directory
cd project/backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt pytest ruff

# Run tests
PYTHONPATH=. pytest tests -v

# Start backend server
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- Documentation (Swagger UI): `http://localhost:8000/api/v1/docs`
- Health check: `http://localhost:8000/health`

### 2. Local Development (Frontend)

```bash
# Serve static frontend
cd project/frontend
python3 -m http.server 3000
# Open http://localhost:3000 in your browser
```

### 3. Containerized Deployment (Podman)

```bash
# From project directory
cp .env.example .env

# Start database, backend, and frontend containers
podman-compose -f deploy/podman-compose.yml up -d

# View running container status
podman ps
```

---

## Documentation Links

- **Architecture Decision Records:** [docs/adr/](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/adr/)
  - [ADR-0001: Three-Tier Architecture](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/adr/0001-three-tier-architecture.md)
  - [ADR-0002: Selection of FastAPI](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/adr/0002-fastapi-backend-framework.md)
  - [ADR-0003: Deferring Secondary Go Edge Service](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/adr/0003-deferring-secondary-go-edge-service.md)
  - [ADR-0004: PostgreSQL and Persistence Strategy](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/adr/0004-postgresql-and-persistence-strategy.md)
  - [ADR-0005: JWT Auth and Password Hashing](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/adr/0005-jwt-auth-and-password-hashing.md)
- **API Reference:** [docs/api/README.md](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/README.md)
  - [OpenAPI Specification (openapi.yaml)](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/openapi.yaml)
  - [POST /api/v1/auth/register](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/register.md)
  - [POST /api/v1/auth/login](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/login.md)
  - [GET /api/v1/auth/me](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/me.md)
