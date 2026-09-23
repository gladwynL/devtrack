# Architecture

## System Overview

DevTrack is two independently deployable applications talking over a REST/JSON API — a React
SPA and a FastAPI backend backed by PostgreSQL. Nothing is shared between them except that
HTTP contract.

```mermaid
flowchart TB
    Browser["Browser<br/>(user)"]

    subgraph Frontend["Frontend — React + TypeScript SPA"]
        SPA["Vite build<br/>served by nginx"]
    end

    subgraph Backend["Backend — FastAPI"]
        API["API layer<br/>app/api/*<br/>(thin route handlers)"]
        Services["Service layer<br/>app/services/*<br/>(business logic, authorization)"]
        ORM["SQLAlchemy models<br/>app/models/*"]
    end

    DB[("PostgreSQL")]

    Browser -- "HTTP" --> SPA
    SPA -- "REST/JSON<br/>Authorization: Bearer &lt;JWT&gt;" --> API
    API --> Services
    Services --> ORM
    ORM -- "SQL" --> DB

    subgraph Infra["Supporting infrastructure"]
        Alembic["Alembic<br/>migrations"]
        CI["GitHub Actions CI<br/>tests · lint · migration check"]
        Docker["Docker / docker-compose<br/>postgres + backend + nginx"]
    end

    Alembic -. "schema changes,<br/>applied explicitly" .-> DB
    CI -. "verifies on every push/PR" .-> Backend
    CI -. " " .-> Frontend
    Docker -. "packages & runs" .-> Backend
    Docker -. "packages & runs" .-> Frontend
```

The backend is layered to keep concerns separated (see the root README for the directory
breakdown): route handlers in `app/api/` never touch the database directly — they call into
`app/services/`, which owns business logic and authorization decisions and is the only layer
that talks to SQLAlchemy models (`app/models/`). Pydantic schemas (`app/schemas/`) are a
distinct concept from ORM models, so what's stored and what's exposed over the API can evolve
independently (e.g. `password_hash` exists on the `User` model but no response schema ever
includes it).

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Backend (/api/auth)
    participant D as PostgreSQL

    U->>F: Enter email + password
    F->>A: POST /api/auth/login
    A->>D: Look up user, verify Argon2 hash
    D-->>A: User row
    A-->>F: JWT access token
    F->>F: Store token in localStorage
    F->>A: Subsequent requests with<br/>Authorization: Bearer &lt;token&gt;
    A->>A: Decode + validate JWT,<br/>load current_user from sub claim
    A-->>F: Response (identity never<br/>taken from the request body)
```

Registration follows the same shape as login, minus the credential check: `POST
/api/auth/register` hashes the password with Argon2 (via `pwdlib`) before it ever touches the
database, and the response schema never includes `password_hash`. A JWT's `sub` claim holds the
user's id; every protected endpoint resolves `current_user` from that claim via a single shared
FastAPI dependency (`app/api/deps.py`) — no endpoint trusts a user id supplied in a request body
or query string for identity purposes.

## Authorization Model

Authorization is enforced in the service layer, not the frontend — the UI hides controls a user
can't use, but every rule is re-checked server-side regardless of what the client sends:

- **Project ownership**: only a project's owner can update it, delete it, or add/remove members.
- **Project membership**: only members can view a project's details, issues, or activity; only
  members can create/update/delete issues within it.
- **Identity derivation**: a project's `owner_id` and an issue's `created_by_id`/activity
  `actor_id` are always derived from the authenticated `current_user`, never accepted as
  client-supplied fields — the request schemas for creating a project or issue don't even have
  those fields.
- **Self-service**: a user can only update or delete their own account.

## Domain Model

```mermaid
erDiagram
    USER ||--o{ PROJECT : owns
    USER ||--o{ PROJECT_MEMBERSHIP : "is a member via"
    PROJECT ||--o{ PROJECT_MEMBERSHIP : has
    PROJECT ||--o{ ISSUE : has
    USER ||--o{ ISSUE : "creates (created_by)"
    USER |o--o{ ISSUE : "assigned to (nullable)"
    ISSUE ||--o{ ISSUE_ACTIVITY : "has history"
    USER |o--o{ ISSUE_ACTIVITY : "acts as (nullable)"

    USER {
        uuid id PK
        string email UK
        string display_name
        string password_hash
    }
    PROJECT {
        uuid id PK
        string name
        string description
        uuid owner_id FK
    }
    PROJECT_MEMBERSHIP {
        uuid id PK
        uuid project_id FK
        uuid user_id FK
        enum role "owner | member"
    }
    ISSUE {
        uuid id PK
        uuid project_id FK
        string title
        string description
        enum status "todo | in_progress | done"
        enum priority "low | medium | high | critical"
        uuid assignee_id FK "nullable"
        uuid created_by_id FK
    }
    ISSUE_ACTIVITY {
        uuid id PK
        uuid issue_id FK
        uuid actor_id FK "nullable"
        enum event_type
        string field_name "nullable"
        string old_value "nullable"
        string new_value "nullable"
    }
```

A few deliberate choices worth calling out:

- **`(project_id, user_id)` is unique** on `PROJECT_MEMBERSHIP` — enforced at the database level
  with a unique constraint, not just in application code, so a user can't be added to the same
  project twice regardless of which code path tries it.
- **Foreign keys use explicit `ON DELETE` behavior**, chosen per relationship rather than left at
  a default: `Project.owner_id` is `RESTRICT` (a user who still owns a project can't be deleted —
  ownership never silently disappears), `Issue.assignee_id` is `SET NULL` (unassigning is a
  normal, harmless outcome of a user being removed), and child rows (`PROJECT_MEMBERSHIP`,
  `ISSUE`, `ISSUE_ACTIVITY`) `CASCADE` from their parent.
- **`ISSUE_ACTIVITY` is scoped to issues only** — it is deliberately not a general-purpose,
  app-wide audit log. Free-text fields (issue description) are recorded as "changed" without
  persisting the actual before/after content, to avoid storing large or sensitive free-form text
  in an append-only log.
- **Status and priority are enum columns with `native_enum=False` and an explicit
  `create_constraint=True`** (see `app/models/enums.py` and the model files), which renders as a
  portable `VARCHAR` + `CHECK` constraint on both SQLite (tests) and PostgreSQL (production),
  rather than a PostgreSQL-native `ENUM` type that would need `ALTER TYPE` migrations to extend
  later.

## Deployment Architecture

```mermaid
flowchart LR
    subgraph Local["Local (docker-compose)"]
        LP[("postgres<br/>container")]
        LB["backend<br/>container"]
        LF["frontend<br/>nginx container"]
        LF --> LB --> LP
    end

    subgraph CI["GitHub Actions"]
        CIB["backend job"]
        CIF["frontend job"]
        CIM["postgres-migrations job<br/>(real postgres service container)"]
    end

    subgraph Prod["Prepared production target (Render)"]
        RP[("Managed PostgreSQL")]
        RB["backend<br/>(Docker web service)"]
        RF["frontend<br/>(static site)"]
        RF --> RB --> RP
    end

    GH["git push"] --> CI
    CI -. "render.yaml Blueprint<br/>(prepared, not yet applied)" .-> Prod
```

Migrations are never run automatically as part of backend startup or a deploy trigger — they're
a deliberate, separate step (`docker compose run --rm migrate` locally; the equivalent one-off
command against whichever database a real deployment uses). See the root README's "Migrations"
section for the full reasoning and exact commands, and [development.md](development.md) for the
day-to-day workflow.
