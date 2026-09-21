# DevTrack

DevTrack is a lightweight project and issue tracking platform, built as a portfolio-quality
full-stack application in the spirit of tools like Jira or Linear.

## Project Status

**Early development.** This repository currently contains only the development foundation:
a running backend and frontend skeleton, database infrastructure, and tooling. No application
features (authentication, projects, issues, comments, dashboards) have been implemented yet.

## Planned Technology Stack

**Frontend**
- React
- TypeScript
- Vite
- Vitest (testing)

**Backend**
- Python
- FastAPI
- SQLAlchemy
- Alembic (database migrations)

**Database**
- PostgreSQL

**Infrastructure**
- Docker / Docker Compose
- GitHub Actions (planned)

**Code quality**
- Ruff (backend linting/formatting)
- ESLint + Prettier (frontend linting/formatting)

## Architecture

DevTrack is split into two independently deployable applications that share nothing but an HTTP
API contract:

```
DevTrack/
├── backend/    FastAPI application (REST API, database access, business logic)
├── frontend/   React single-page application
└── docker-compose.yml   Local PostgreSQL instance
```

The backend follows a layered structure to keep concerns separated:

- `app/api/` — route handlers (HTTP concerns only)
- `app/services/` — business logic, called by route handlers
- `app/models/` — SQLAlchemy ORM models (database layer)
- `app/schemas/` — Pydantic schemas (request/response validation, separate from ORM models)
- `app/core/` — configuration and cross-cutting concerns
- `app/db/` — database engine/session setup

Configuration is environment-variable-driven on both sides; no secrets are committed to the
repository (see `.env.example`).

## Local Development Prerequisites

- Python 3.12+
- Node.js 20+
- Docker and Docker Compose (for PostgreSQL)

## Getting Started

1. Copy the environment template and adjust as needed:

   ```bash
   cp .env.example .env
   ```

2. Start PostgreSQL:

   ```bash
   docker compose up -d
   ```

3. Set up and run the backend:

   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   pip install -r requirements-dev.txt
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`, with a health check at
   `http://localhost:8000/health`.

4. Set up and run the frontend (in a separate terminal):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   The app will be available at `http://localhost:5173`.

## Running Tests

```bash
# Backend
cd backend
venv\Scripts\pytest

# Frontend
cd frontend
npm run test
```

## Code Quality

```bash
# Backend (from backend/)
venv\Scripts\python -m ruff check .
venv\Scripts\python -m ruff format .

# Frontend (from frontend/)
npm run lint
npm run format
```

## License

MIT — see [LICENSE](LICENSE).
