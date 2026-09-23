# DevTrack

DevTrack is a lightweight project and issue tracking platform, built as a portfolio-quality
full-stack application in the spirit of tools like Jira or Linear.

## Project Status

**Early development, but usable end-to-end.** You can register, log in, create and delete
projects, manage project members, and create/edit/assign/delete issues entirely through the
web UI, backed by a JWT-authenticated REST API. Issues can be searched, filtered, and sorted,
and each issue has a lightweight activity history (who created it, and what changed since).
Comments, analytics, advanced search, and deployment/CI are not implemented yet.

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

## Authentication

The API uses password-based registration/login and short-lived JWT bearer tokens:

- `POST /api/auth/register` — create an account (email, display name, password)
- `POST /api/auth/login` — exchange credentials for an access token
- `GET /api/auth/me` — resolve the current user from a bearer token

Passwords are hashed with Argon2 (via `pwdlib`) and never stored or returned in plaintext.
Protected endpoints require an `Authorization: Bearer <token>` header. Project- and
issue-level access is scoped to project membership; only a project's owner can update or
delete it, or add/remove members. `JWT_SECRET_KEY`, `JWT_ALGORITHM`, and
`JWT_ACCESS_TOKEN_EXPIRE_MINUTES` are configured via environment variables — see
`.env.example`. The backend ships with an insecure development default secret key so local
setup works without a `.env` file; any real deployment must override it.

## Issue Activity

Each issue keeps a lightweight, append-only activity log (`GET /api/issues/{issue_id}/activity`,
members only) recording creation and changes to title, description, status, priority, and
assignee. It's intentionally scoped to issues, not a general-purpose audit system: description
changes are recorded as an event without storing the actual before/after text, to avoid
retaining large or sensitive free-form content. If a user who authored an activity entry is
later deleted, the entry is kept with a null actor rather than being deleted itself or blocking
the deletion.

List endpoints (`/api/users`, `/api/projects`, `/api/projects/{id}/issues`,
`/api/issues/{id}/activity`) validate `limit` (1–200) and `offset` (≥0). Issue search, filtering,
and sorting are done client-side over a project's already-loaded issue list rather than via
additional API round-trips — reasonable at this project's scale, and the service layer already
takes `limit`/`offset` so it can move server-side later without an API shape change.

## Frontend

A single-page React app provides the full authenticated workflow: registration, login,
logout, a project dashboard, project detail (with member management and deletion for owners),
and issue creation/editing/assignment/deletion, with search, status/priority/assignee filters,
and sorting (newest, oldest, priority, status). Routing is handled by React Router;
unauthenticated visitors are redirected to `/login`, and already-authenticated visitors are
kept off `/login`/`/register`. Destructive actions (deleting an issue or a project) go through
a shared, keyboard-accessible confirmation dialog rather than the browser's native `confirm()`.

- **Session**: on login/register, the API's JWT is stored in `localStorage` and attached as a
  `Bearer` token to every subsequent request. On load, the app calls `GET /api/auth/me` to
  restore the session; an invalid or expired token clears itself and returns the user to
  `/login`. The token is never put in a URL or logged to the console.
- **API client**: `src/api/client.ts` centralizes the base URL (`VITE_API_BASE_URL`, see
  `frontend/.env.example`), auth headers, and JSON/error parsing, so feature code just calls
  typed functions like `createIssue(projectId, values)`.
- **Authorization UX**: the frontend hides owner-only controls (edit project, add/remove
  member) from non-owners and reflects project membership in what's shown, but the backend
  remains the source of truth — every rule is enforced there regardless of what the UI shows.
- Structure: `src/api/` (HTTP calls), `src/features/<domain>/` (forms and domain UI),
  `src/pages/` (routed pages), `src/components/` (shared UI), `src/types/` (API-aligned
  domain types), `src/hooks/` (small reusable hooks).

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

   The app will be available at `http://localhost:5173` and defaults to talking to the API at
   `http://localhost:8000`. To point it elsewhere, copy `frontend/.env.example` to
   `frontend/.env.local` and set `VITE_API_BASE_URL`.

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
