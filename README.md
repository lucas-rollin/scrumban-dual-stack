# Scrumban Dual Stack

*Status: Active Development. Django domain modeling in progress, FastAPI implementation coming next.*

A comparative full-stack project management application implemented with **Django REST Framework** and **FastAPI + SQLAlchemy**, sharing the same PostgreSQL instance with different databases and consumed by the same React + TypeScript frontend.

This project is a **practical reference for developers who know one Python web stack and want to learn the other**. Rather than a lightweight demo, both backends target the same application capabilities using the idiomatic patterns, testing strategies, and ORM conventions of their respective ecosystems.

## Why This Project?

Most tutorials present Django or FastAPI in isolation, often relying on flat project structures. **Scrumban Dual Stack** demonstrates how both ecosystems grow into production-ready architectures featuring non-trivial domain logic, query optimization, authentication, and database integrity.

## Architecture

The project consists of one frontend and two independent backend implementations:

```text
                    React + TypeScript
                           │
                    common API contract
                           │
             ┌─────────────┴─────────────┐
             │                           │
       Django + DRF                   FastAPI
             │                           │
       Django ORM                     SQLAlchemy
             │                           │
       Django migrations              Alembic
             │                           │
             └─────────────┬─────────────┘
                           │
                Same PostgreSQL instance
                  (separate databases)
```

Each backend has its own database so that its schema and migration history can evolve independently. The frontend is designed to consume either backend, making the implementations directly comparable without requiring two separate clients.

## Project Structure

The repository keeps the backend implementations physically separate while organizing each according to the conventions of its ecosystem.

```text
.
├── backend-django/
│   ├── apps/
│   │   ├── accounts/
│   │   └── scrumban/
│   └── config/
│
├── backend-fastapi/
│   ├── alembic/
│   └── app/
│       ├── core/
│       ├── accounts/
│       └── scrumban/
│
├── frontend/
├── postgres/
├── docker-compose.yml
└── docker-compose.prod.yml
```

### Django

The Django backend uses Django's application-oriented structure. Domain functionality is grouped into Django apps, a good practice for scalable projects to not polute the root namespace, while project-level configuration lives in `config/`.

### FastAPI

The FastAPI backend separates application-wide concerns into `core/` and domain functionality into feature-oriented apps under `accounts/` and `scrumban/`.

The structures are intentionally **conceptually parallel without being identical**. Equivalent concerns should be easy to locate between the two backends, but each implementation follows the conventions of its framework rather than imitating the other.

As the application grows, additional layers will be introduced when they solve an actual problem rather than being added purely for architectural ceremony.

## Domain Model

Scrumban Dual Stack models a collaborative project-management workspace combining Kanban flow with optional Scrum-style sprints.

The core hierarchy is:

```text
Workspace
├── Members
├── Labels
└── Boards
    ├── Columns
    │   └── Tasks         
    │       ├── Subtasks 
    │       ├── Labels
    │       ├── Assignee
    │       ├── Comments
    │       └── Activity
    │
    └── Sprints
        └── Tasks
```

A **Workspace** contains members, boards, and reusable labels. A **Board** defines the workflow through ordered columns and can optionally organize work into sprints.

A **Task** belongs to a column and may optionally belong to a sprint. Tasks can be assigned to users, tagged with labels, organized into parent/subtask relationships, commented on, and tracked through activity records.

The domain intentionally includes database constraints, hierarchical relationships, many-to-many relationships, optional relationships, ordering, historical activity, and query-oriented indexes.

For the complete relational model, see [Domain Model / ERD](docs/architecture/erd.md).

## Docker Architecture & Environments

Every service uses a **single multi-stage `Dockerfile`** with dedicated `development` and `production` build targets. Dependency management is handled by **`uv`** for Python backends and **`pnpm`** for the React frontend.

| Service | Development Target (`development`) | Production Target (`production`) |
| --- | --- | --- |
| **Django** (`backend-django`) | Live reload (`runserver`), bind-mounted source, anonymous volume for `/app/.venv` | Multi-stage, non-root `appuser`, `gunicorn`, static asset collection |
| **FastAPI** (`backend-fastapi`) | Live reload (`fastapi dev`), bind-mounted source, anonymous volume for `/app/.venv` | Multi-stage, non-root `appuser`, `uvicorn` |
| **Frontend** (`frontend`) | Live reload (`vite`), bind-mounted source, anonymous volume for `/app/node_modules` | Multi-stage, static bundle built with `pnpm build` and served via Nginx Alpine |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed **(required for the recommended workflow)**
- Git (optional, for cloning)

## Quick Start

### Docker Compose

#### 1. Clone & Configure Environment Variables

```bash
git clone https://github.com/lucas-rollin/scrumban-dual-stack.git
cd scrumban-dual-stack

# Root config (Postgres superuser credentials for DB & Adminer)
cp .env.example .env

# Backend configs
cp backend-django/.env.example backend-django/.env
cp backend-fastapi/.env.example backend-fastapi/.env
cp frontend/.env.example frontend/.env
```

*(Update these files with your preferred local values before continuing).*

#### 2. Start Services

```bash
docker compose up -d
```

#### 3. Run Database Migrations

Once the containers are running, apply the database schemas:

- **Django:**

    ```bash
    docker compose exec backend-django python manage.py migrate
    ```

- **FastAPI:**

    ```bash
    docker compose exec backend-fastapi alembic upgrade head
    ```

#### 4. Verify

Run `docker compose ps` to ensure all containers are running. Access the endpoints at:

- **Django:** [http://localhost:8000](http://localhost:8000)
- **FastAPI:** [http://localhost:8001](http://localhost:8001)
- **React:** [http://localhost:5173](http://localhost:5173)
- **Adminer:** [http://localhost:8080](http://localhost:8080) *(Server: `db`)*

> **Troubleshooting:** If you encounter issues with the containerized setup, or need to run applications locally for debugging, see the [Local Development](#local-development-alternative) section below.

### Local Development (Alternative)

#### Option A: Running the Database via Docker (Recommended fallback)

This is the recommended alternative when you want to run the application processes directly on your host while keeping PostgreSQL containerized.

Start only the PostgreSQL database and Adminer:

```bash
docker compose up -d db adminer
```

#### Option B: Running Local PostgreSQL (Advanced users only)

If you prefer a native PostgreSQL server on your host:

1. Ensure PostgreSQL is running on port 5432.
2. Create the two databases:

   ```sql
   CREATE DATABASE scrumban_django;
   CREATE DATABASE scrumban_fastapi;
   ```

3. Update `DATABASE_URL` in `backend-django/.env` and `backend-fastapi/.env` with your local credentials.

#### 1. Django Backend (backend-django)

```bash
cd backend-django

# Prepare environment
cp .env.example .env

# Install dependencies with uv
uv sync

# Apply database migrations
uv run python manage.py migrate

# Start the development server (port 8000)
uv run python manage.py runserver 8000
```

Access Django at [http://127.0.0.1:8000](http://127.0.0.1:8000).

#### 2. FastAPI Backend (backend-fastapi)

> **Note:** FastAPI uses port 8001 to match the project's frontend/API configuration.

```bash
cd backend-fastapi

# Prepare environment
cp .env.example .env

# Install dependencies with uv
uv sync

# Run Alembic migrations
uv run alembic upgrade head

# Start FastAPI dev server on port 8001
uv run fastapi dev --port 8001
```

Access FastAPI at [http://127.0.0.1:8001](http://127.0.0.1:8001) and Swagger docs at [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs).

#### 3. React Frontend (frontend)

```bash
cd frontend

# Install dependencies
pnpm install

# Start Vite dev server
pnpm dev
```

Access the frontend at [http://localhost:5173](http://localhost:5173).

## Production Deployment

To run the full application using the production targets (`target: production`):

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

In production mode:

- Backends run under a non-root user (`appuser`) using production WSGI/ASGI servers (`gunicorn` / `uvicorn`).
- No host source directories are mounted into `/app`.
- Static files for Django are collected into WhiteNoise storage during image build.
- The React frontend is compiled to static files and served directly by Nginx.

## Database Management

The PostgreSQL databases are initialized automatically on first startup of a new Docker volume via `postgres/init-db.sql`.

To completely reset the database volumes (e.g., after modifying initialization scripts):

```bash
docker compose down -v
docker compose up -d db
```

## Dependency Management

### Python Backends (uv)

Dependencies are managed using pyproject.toml and locked with uv.lock.

- Install / sync local environment:

    ```bash
    cd backend-django   # or cd backend-fastapi
    uv sync
    ```

- Add a runtime dependency:

    ```bash
    uv add <package_name>
    ```

- Add a development dependency:

    ```bash
    uv add --dev <package_name>
    ```

- Update lockfile:

    ```bash
    uv lock --upgrade
    ```

> **Note:** During development with Docker Compose, an anonymous volume (`/app/.venv`) protects the container's virtual environment from host mounts. If you add or remove packages via `uv` on your host machine, rebuild the development containers
> so Docker updates the internal virtual environment:
>
> ```bash
> docker compose up -d --build backend-django backend-fastapi
> ```

### Frontend (pnpm)

Dependencies are managed using `package.json` and locked with `pnpm-lock.yaml`.

- Install / sync local environment:

    ```bash
    cd frontend
    pnpm install
    ```

- Add a runtime dependency:

    ```bash
    pnpm add <package_name>
    ```

- Add a development dependency:

    ```bash
    pnpm add -D <package_name>
    ```

- Update dependencies and lockfile:

    ```bash
    pnpm update
    ```

> **Note:** Similar to the backend workflow, if you run the frontend through Docker Compose, `node_modules` is typically managed inside the container. If you install or update packages on your host machine, you will need to rebuild the frontend container:
>
> ```bash
> docker compose up -d --build frontend
> ```
