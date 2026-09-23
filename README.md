# DevTrack

DevTrack is a lightweight project and issue tracking platform, built as a portfolio-quality
full-stack application in the spirit of tools like Jira or Linear.

## Project Status

**Early development, but usable end-to-end and container-ready.** You can register, log in,
create and delete projects, manage project members, and create/edit/assign/delete issues
entirely through the web UI, backed by a JWT-authenticated REST API. Issues can be searched,
filtered, and sorted, and each issue has a lightweight activity history. The full stack
(PostgreSQL, backend, frontend) runs in Docker, migrations are verified against real
PostgreSQL, and CI runs on every push/PR. **It is not deployed anywhere right now** — see
[Deployment](#deployment) for what's prepared and what's left. Comments, analytics, and
advanced search are not implemented yet.

## Technology Stack

**Frontend**
- React, TypeScript, Vite
- Vitest (testing)

**Backend**
- Python, FastAPI, SQLAlchemy
- Alembic (database migrations)

**Database**
- PostgreSQL

**Infrastructure**
- Docker / Docker Compose (backend, frontend, and PostgreSQL all containerized)
- GitHub Actions CI (backend tests/lint, frontend tests/build/lint, migrations against real
  PostgreSQL)

**Code quality**
- Ruff (backend linting/formatting)
- ESLint + Prettier (frontend linting/formatting)

## Architecture

DevTrack is split into two independently deployable applications that share nothing but an HTTP
API contract:

```
DevTrack/
├── backend/              FastAPI application (REST API, database access, business logic)
│   ├── Dockerfile        Production image (plain uvicorn, non-root user)
│   └── alembic/          Migrations
├── frontend/             React single-page application
│   ├── Dockerfile        Production image (Vite build → static files served by nginx)
│   └── nginx.conf        SPA routing fallback + static asset caching
├── .github/workflows/    CI (backend, frontend, migrations-against-Postgres jobs)
├── docker-compose.yml    Full local stack: postgres + backend + frontend
└── render.yaml           Deployment blueprint (prepared, not yet applied — see Deployment)
```

The backend follows a layered structure to keep concerns separated:

- `app/api/` — route handlers (HTTP concerns only)
- `app/services/` — business logic, called by route handlers
- `app/models/` — SQLAlchemy ORM models (database layer)
- `app/schemas/` — Pydantic schemas (request/response validation, separate from ORM models)
- `app/core/` — configuration and cross-cutting concerns
- `app/db/` — database engine/session setup

Configuration is environment-variable-driven on both sides; no secrets are committed to the
repository (see [Environment Variables](#environment-variables)).

## Authentication

The API uses password-based registration/login and short-lived JWT bearer tokens:

- `POST /api/auth/register` — create an account (email, display name, password)
- `POST /api/auth/login` — exchange credentials for an access token
- `GET /api/auth/me` — resolve the current user from a bearer token

Passwords are hashed with Argon2 (via `pwdlib`) and never stored or returned in plaintext.
Protected endpoints require an `Authorization: Bearer <token>` header. Project- and
issue-level access is scoped to project membership; only a project's owner can update or
delete it, or add/remove members. If `ENVIRONMENT=production`, the app refuses to start unless
`JWT_SECRET_KEY` has been overridden from its (insecure, dev-only) built-in default.

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
- **API client**: `src/api/client.ts` centralizes the base URL (`VITE_API_BASE_URL`), auth
  headers, and JSON/error parsing, so feature code just calls typed functions like
  `createIssue(projectId, values)`.
- **`VITE_API_BASE_URL`**: Vite bakes this into the JS bundle at *build* time — there's no
  runtime env to change afterward in the browser. It must be a URL the end user's browser can
  reach, never a Docker-internal service name like `http://backend:8000`. See
  `frontend/.env.example` for local dev and [Docker](#docker--local-production-style-stack) /
  [Deployment](#deployment) for how it's set in those contexts.
- **Authorization UX**: the frontend hides owner-only controls (edit project, add/remove
  member) from non-owners and reflects project membership in what's shown, but the backend
  remains the source of truth — every rule is enforced there regardless of what the UI shows.
- Structure: `src/api/` (HTTP calls), `src/features/<domain>/` (forms and domain UI),
  `src/pages/` (routed pages), `src/components/` (shared UI), `src/types/` (API-aligned
  domain types), `src/hooks/` (small reusable hooks).

## Health Checks

- `GET /health` — **liveness**. Is the process up? Deliberately cheap: no database call, no
  external dependency.
- `GET /ready` — **readiness**. Is the process up *and* can it reach the database? Runs
  `SELECT 1`; returns `503` if the database is unreachable.

Docker Compose's backend healthcheck (and, in a real deployment, an orchestrator's readiness
probe) should point at `/ready`, since that's the one that actually confirms the service can
serve real requests.

## Local Development Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop (for PostgreSQL, and optionally the full containerized stack)

## Getting Started (running services natively)

This is the fastest loop for day-to-day backend/frontend development, with only PostgreSQL in
Docker.

1. Copy the environment template and adjust as needed:

   ```bash
   cp .env.example .env
   ```

2. Start PostgreSQL:

   ```bash
   docker compose up -d postgres
   ```

3. Apply migrations (see [Migrations](#migrations) for the reasoning):

   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   pip install -r requirements-dev.txt
   python -m alembic upgrade head
   ```

4. Run the backend:

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000` (`/health`, `/ready`).

5. Set up and run the frontend (in a separate terminal):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   The app will be available at `http://localhost:5173` and defaults to talking to the API at
   `http://localhost:8000`. To point it elsewhere, copy `frontend/.env.example` to
   `frontend/.env.local` and set `VITE_API_BASE_URL`.

## Docker / Local Production-Style Stack

To run the whole stack the way it would run in production — containerized backend and
frontend, both talking to containerized PostgreSQL over Docker networking:

```bash
# 1. Build all three images
docker compose build

# 2. Apply migrations once (see Migrations below for why this is a separate step)
docker compose run --rm migrate

# 3. Start postgres + backend + frontend
docker compose up -d

# 4. Check status / health
docker compose ps
curl http://localhost:8000/ready
```

- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432` (same credentials as `.env.example`)

`docker compose ps` should show `postgres` and `backend` as `healthy` (their Dockerfiles/compose
config define real healthchecks; `frontend` has none defined since a static nginx server has
little to meaningfully fail on). PostgreSQL data persists in the named `postgres_data` volume
across `docker compose down` (without `-v`) and container restarts.

Stop everything without deleting data:

```bash
docker compose down
```

Only delete the database volume if you explicitly want a clean slate:

```bash
docker compose down -v
```

### Why the frontend needs `FRONTEND_API_BASE_URL`, not just `VITE_API_BASE_URL`

The frontend container is built with `VITE_API_BASE_URL` set to `http://localhost:8000` by
default (see `FRONTEND_API_BASE_URL` in `.env.example`), **not** `http://backend:8000`. Vite
bakes this value into the JS bundle that runs in the browser on the host machine — the browser
has no access to the `devtrack` Docker network, so a Docker service name would simply fail to
resolve. `docker-compose.yml` documents this inline as well.

## Migrations

**Migrations are never run automatically on container/app startup.** They're a deliberate,
explicit step, run once per schema change, so a failure is visible and attributable rather than
hidden inside app boot (and so multiple backend replicas never race each other running
`alembic upgrade head` concurrently).

```bash
# Natively (with PostgreSQL running, e.g. via `docker compose up -d postgres`)
cd backend
python -m alembic upgrade head

# Via Docker Compose (no local Python/venv needed)
docker compose run --rm migrate
```

New migrations are still generated the normal Alembic way (`alembic revision --autogenerate`)
against a running database, and are reviewed by hand before committing — see the migration
files under `backend/alembic/versions/` for the established pattern (portable
`native_enum=False` enum columns with explicit `create_constraint=True`, explicit `ondelete`
behavior on every foreign key).

## Running Tests

```bash
# Backend (fast, SQLite-backed — no services required)
cd backend
venv\Scripts\pytest

# Frontend
cd frontend
npm run test
```

One backend test is intentionally **not** part of that fast run:
`tests/test_postgres_integration.py` exercises the real service layer (ORM + Argon2 hashing)
against actual PostgreSQL, and only runs when `POSTGRES_TEST_DATABASE_URL` is set:

```bash
docker compose up -d postgres
cd backend
POSTGRES_TEST_DATABASE_URL=postgresql+psycopg2://devtrack:devtrack@localhost:5432/devtrack \
    venv\Scripts\python -m pytest tests/test_postgres_integration.py -v
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

## Continuous Integration

`.github/workflows/ci.yml` runs on every push and pull request to `main`, as three independent
jobs:

- **backend** — installs `requirements-dev.txt`, runs `pytest`, `ruff check`, `ruff format --check`
- **frontend** — `npm ci`, `npm run test`, `npm run build`, `npm run lint`, `npm run format:check`
- **postgres-migrations** — spins up a real `postgres:16-alpine` service container, then runs
  `alembic upgrade head` → `alembic downgrade base` → `alembic upgrade head` (proving the full
  chain applies *and* fully reverses), followed by the PostgreSQL integration test

No production secrets are required for CI — the Postgres job uses throwaway, CI-only
credentials that only ever exist inside that job's service container.

## Environment Variables

See `.env.example` (local dev / docker-compose) and `.env.production.example` (deployment
template) for full templates with comments. Summary:

| Variable                          | Used by          | Notes                                                              |
| ---------------------------------- | ----------------- | -------------------------------------------------------------------- |
| `DATABASE_URL`                     | backend           | Normalized to `postgresql+psycopg2://` regardless of input scheme  |
| `ENVIRONMENT`                      | backend           | `development` (default) or `production`                            |
| `DEBUG`                            | backend           | Defaults to `false`; enables FastAPI debug tracebacks if `true`    |
| `CORS_ORIGINS`                     | backend           | JSON array of allowed frontend origins — never `*`                 |
| `JWT_SECRET_KEY`                   | backend           | Required (non-default) when `ENVIRONMENT=production`               |
| `JWT_ALGORITHM`                    | backend           | Default `HS256`                                                    |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`  | backend           | Default `30`                                                       |
| `VITE_API_BASE_URL`                | frontend (build)  | Baked in at build time — must be browser-reachable                 |
| `POSTGRES_USER/PASSWORD/DB/PORT`   | docker-compose    | Local PostgreSQL container only                                    |
| `BACKEND_PORT` / `FRONTEND_PORT`   | docker-compose    | Host ports for the full stack (default `8000` / `8080`)            |
| `FRONTEND_API_BASE_URL`            | docker-compose    | Passed to the frontend build as `VITE_API_BASE_URL`                |

## Deployment

**Not deployed anywhere yet.** This environment has no accounts or credentials for a hosting
platform, so nothing has been (or could honestly be) deployed from here. What's prepared:

- `render.yaml` — a [Render Blueprint](https://render.com/docs/blueprint-spec) describing three
  resources: managed PostgreSQL, the backend as a Docker web service (`backend/Dockerfile`,
  healthcheck at `/ready`), and the frontend as a static site (`npm run build`, SPA rewrite
  rule) — chosen because it needs one platform account rather than juggling several, keeps the
  managed-Postgres/backend/frontend trio together, and doesn't require running an nginx
  container just to serve static files.
- Both Dockerfiles are platform-agnostic (no Render-specific assumptions baked in), so the same
  images work on any container host if a different platform is preferred later.

**Remaining manual steps** (require a human with account access):

1. Create a Render account and connect this GitHub repository.
2. Apply the Blueprint (`render.yaml`) — Render provisions the database and both services.
3. After the first deploy, copy the real assigned URLs into `CORS_ORIGINS` (backend) and
   `VITE_API_BASE_URL` (frontend build env var), since a Blueprint can't reference a sibling
   service's URL before it exists — then redeploy both.
4. Run migrations against the new database once:
   `DATABASE_URL=<Render's connection string> python -m alembic upgrade head` (or via a Render
   one-off job), matching the same "explicit step, not automatic" policy used locally.

No deployment URL exists to link here — this README will be updated with one only once a real
deployment exists.

## License

MIT — see [LICENSE](LICENSE).
