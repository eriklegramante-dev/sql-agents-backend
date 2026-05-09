# SQL Agents Backend

Backend API for the SQL Agents Platform. The project provides user management,
JWT authentication, role-based access control, database migrations, and a
FastAPI foundation for the platform services.

## Tech Stack

- Python 3.10
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic Settings
- JWT authentication
- Docker and Docker Compose
- Pytest

## Requirements

- Python 3.10+
- Poetry
- Docker
- Docker Compose

## Setup

Clone the repository:

```bash
git clone git@github.com:Huelerssey/sql-agents-backend.git
cd sql-agents-backend
```

Install dependencies with Poetry:

```bash
poetry install
```

Poetry creates and manages the project virtual environment automatically. The
project also declares `poetry-plugin-shell` as a required Poetry plugin, so
`poetry install` installs it for this project when needed.

`poetry run` must always receive the command that should run inside the project
environment:

```bash
poetry run pytest
```

To activate the virtual environment in the current shell, run:

```bash
eval "$(poetry env activate)"
```

In Poetry 2.x, `poetry shell` is no longer installed by default. This project
enables it through `poetry-plugin-shell`, so after `poetry install` you can also
activate the environment with:

```bash
poetry shell
```

After activation, commands can be executed without the `poetry run` prefix:

```bash
pytest
```

## Pre-commit

Install the Git hooks once after cloning the project:

```bash
poetry run python -m pre_commit install
```

This command only needs to be executed one time per local clone. After that,
pre-commit runs automatically on `git commit`.

To run all configured hooks manually against the whole project:

```bash
poetry run python -m pre_commit run --all-files
```

Create the local environment file:

```bash
cp .env.example .env
```

The default `.env.example` values are ready for local development with Docker
Compose. Update secrets before using any production-like environment.

## Environment Variables

| Variable | Description |
| --- | --- |
| `APP_ENVIRONMENT` | Application environment. Use `dev` for local development. |
| `POSTGRES_USER` | PostgreSQL username used by Docker Compose. |
| `POSTGRES_PASSWORD` | PostgreSQL password used by Docker Compose. |
| `POSTGRES_DB` | PostgreSQL database name used by Docker Compose. |
| `DATABASE_URL_DEV` | Local development database URL. |
| `DATABASE_URL_PROD` | Production database URL. |
| `SENTRY_DNS` | Sentry DSN for error tracking. |
| `SECURITY_SECRET_KEY` | Secret key used to sign JWT tokens. |
| `SECURITY_JWT_ALGORITHM` | JWT signing algorithm. |
| `SECURITY_JWT_EXP_MINUTES` | JWT expiration time in minutes. |

## Run Project (Docker)

Start the API and database:

```bash
docker compose up --build -d
```

Run database migrations:

```bash
docker compose exec fast-api-crud alembic upgrade head
```

The API will be available at:

```text
http://localhost:8000
```

Open the interactive API documentation:

```text
http://localhost:8000/docs
```
