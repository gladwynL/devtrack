# API Overview

The backend exposes a REST/JSON API under the `/api` prefix (health checks are the one
exception — see below). For the full request/response schema of every endpoint, run the backend
and open the interactive OpenAPI docs at **`/docs`** (Swagger UI) or **`/redoc`**; this page is a
map, not a replacement for that.

## Authentication

Every endpoint except registration, login, and the two health checks requires a JWT bearer
token:

```
Authorization: Bearer <token>
```

Obtain a token from `POST /api/auth/login` (or `/api/auth/register`, which logs the new user in
immediately). Tokens are opaque to the client — the frontend never decodes them, it just stores
and forwards the string. A missing or invalid token returns `401`; a valid token for a user who
isn't authorized for the specific resource (e.g. not a project member) returns `403`.

## Route Groups

| Group | Prefix | Auth required | Notes |
|---|---|---|---|
| Health | `/health`, `/ready` | No | Liveness vs. readiness (DB connectivity) — see below. |
| Auth | `/api/auth` | Mixed | `register`/`login` are public; `me` requires a token. |
| Users | `/api/users` | Yes | List/view/update/delete accounts; self-service only for update/delete. |
| Projects | `/api/projects` | Yes | Create/list/view/update/delete; view/update/delete scoped to owner or members. |
| Memberships | `/api/projects/{project_id}/members` | Yes | List/add/remove members; add/remove restricted to the project owner. |
| Issues | `/api/projects/{project_id}/issues`, `/api/issues/{issue_id}` | Yes | Create/list/view/update/delete issues, plus per-issue activity history. |

### Health

- `GET /health` — cheap liveness check, always returns `200` if the process is up. Used for
  container liveness probes.
- `GET /ready` — readiness check that runs `SELECT 1` against the database and returns `503` if
  it fails. Used for container/orchestrator readiness gating and by `docker-compose`'s backend
  healthcheck.

### Auth (`/api/auth`)

- `POST /register` — create an account (email, display name, password). Password is hashed with
  Argon2 before storage; the response never includes the hash.
- `POST /login` — exchange email + password for a JWT access token.
- `GET /me` — return the authenticated user's own profile, resolved from the token.

### Users (`/api/users`)

- `GET /` — list users (used for member-picker UI when adding project members).
- `GET /{user_id}` — view a single user.
- `PATCH /{user_id}` — update a user. Restricted to updating your own account.
- `DELETE /{user_id}` — delete a user. Restricted to your own account; blocked at the database
  level if the account still owns a project (`RESTRICT` foreign key).

### Projects (`/api/projects`)

- `POST /` — create a project. The creator becomes the owner automatically; there is no
  client-supplied owner field.
- `GET /` — list projects the authenticated user is a member of.
- `GET /{project_id}` — view a project. Requires membership.
- `PATCH /{project_id}` — update a project's name/description. Owner only.
- `DELETE /{project_id}` — delete a project (cascades to its memberships, issues, and issue
  activity). Owner only.

### Memberships (`/api/projects/{project_id}/members`)

- `GET /` — list a project's members and their roles. Requires membership.
- `POST /` — add a member by user id. Owner only.
- `DELETE /{user_id}` — remove a member. Owner only.

### Issues (`/api/projects/{project_id}/issues`, `/api/issues/{issue_id}`)

- `POST /projects/{project_id}/issues` — create an issue in a project. Requires membership; the
  creator is recorded automatically as `created_by`.
- `GET /projects/{project_id}/issues` — list a project's issues. Requires membership.
- `GET /issues/{issue_id}` — view a single issue. Requires membership in its project.
- `PATCH /issues/{issue_id}` — update title, description, status, priority, or assignee.
  Requires membership; each changed field is recorded as an activity entry.
- `DELETE /issues/{issue_id}` — delete an issue (cascades to its activity history). Requires
  membership.
- `GET /issues/{issue_id}/activity` — chronological activity log for the issue (created,
  status/priority/assignee changes, etc). Requires membership.

## Common Status Codes

| Code | Meaning here |
|---|---|
| `200` | Successful read or update. |
| `201` | Resource created (register, create project, create issue, add member). |
| `204` | Successful delete — no response body. |
| `400` | Validation error (e.g. malformed input, business-rule violation). |
| `401` | Missing, malformed, or expired JWT. |
| `403` | Valid token, but the user isn't authorized for this resource (not a member/owner). |
| `404` | Resource doesn't exist. |
| `409` | Conflict (e.g. duplicate email on registration, user already a project member). |
| `422` | Request body failed schema validation (FastAPI/Pydantic default). |
| `503` | `/ready` only — database is unreachable. |

These map 1:1 to a small custom exception hierarchy in the service layer
(`NotFoundError`, `ConflictError`, `ValidationError`, `AuthenticationError`,
`AuthorizationError`) translated to HTTP responses by exception handlers in `app/main.py`, which
keeps route handlers free of manual status-code logic. See [architecture.md](architecture.md)
for how the layers fit together.
