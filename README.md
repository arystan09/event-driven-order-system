# Event-Driven Backend

Initial project scaffold for an event-driven order processing backend with FastAPI, PostgreSQL, and Redis.

## Structure

- `app/api` - API routers and endpoints
- `app/services` - business logic services
- `app/repositories` - persistence abstraction layer
- `app/db` - database session and setup
- `app/models` - domain and ORM models
- `worker` - background consumer process

## Run API

```bash
uvicorn app.main:app --reload
```

## Run Worker

```bash
python -m worker.main
```

## Migrations (Alembic)

Run migrations locally (requires Postgres running and `psycopg2-binary` installed):

```bash
alembic -c alembic.ini upgrade head
```

## Run with Docker

```bash
docker compose up --build
```

Then apply migrations from another shell:

```bash
docker compose exec api alembic -c alembic.ini upgrade head
```
