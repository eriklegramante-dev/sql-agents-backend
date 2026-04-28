# SQL Agents Backend

Backend CRUD built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, and JWT authentication.

## Running with Docker

Start the full local stack:

```bash
docker compose up -d --build
```

Run database migrations from your local terminal:

```bash
alembic upgrade head
```

Open the API docs:

```text
http://localhost:8000/docs
```

## Local Development Notes

The `.env` file is prepared for local commands to reach PostgreSQL through the Docker-exposed port:

```text
DATABASE_URL_DEV=postgresql+asyncpg://crud_user:123456789abcde@localhost:5432/crud_fastapi
```

Inside Docker Compose, the API service overrides this value to use the internal service hostname:

```text
DATABASE_URL_DEV=postgresql+asyncpg://crud_user:123456789abcde@postgres:5432/crud_fastapi
```

Use `.env.example` as the reference file for new local environments.

## First Admin User

Protected create routes require an authenticated admin user. For a fresh database, run the bootstrap command documented in `BOOTSTRAP_ADMIN.md` after applying migrations.
