# CodeVector Products API

Small FastAPI backend for browsing a 200,000-row products table with stable keyset pagination.

Bonus UI available at `/browse`.

## What it does

- `GET /products`
- Filter by `category`
- Paginate with a cursor based on `updated_at DESC, id DESC`
- Freeze a browse session with a snapshot timestamp so new writes do not reshuffle the result set

## Architecture

- **FastAPI** for the HTTP layer
- **PostgreSQL** as the storage engine
- **SQLAlchemy** for models and queries
- **Alembic** for schema migrations
- **psycopg** as the PostgreSQL driver

The app keeps the code small on purpose: one table, one endpoint, one seed script, and one migration.

## Pagination strategy

The API does not use `OFFSET`.

It uses keyset pagination with the ordering:

1. `updated_at DESC`
2. `id DESC`

The cursor stores the last seen `(updated_at, id)` pair plus a snapshot timestamp. Each page applies:

- `updated_at <= snapshot`
- `updated_at < last_updated_at OR (updated_at = last_updated_at AND id < last_id)`

That gives stable paging order and avoids duplicate rows when the user moves through pages.

The snapshot timestamp is returned with the first page and embedded in the cursor so the same browse session keeps reading the same logical slice of data.

## Indexes

The migration creates two PostgreSQL indexes:

- `(updated_at DESC, id DESC)` for the base ordered browse path
- `(category, updated_at DESC, id DESC)` for category-filtered browsing

These match the access pattern used by the endpoint and keep the query planner on an index-driven plan instead of sorting a large working set.

## Tradeoffs

- Snapshot-based browsing is simple and fast, but it is not a full historical MVCC view. If a product is updated after a user starts browsing, that product may move out of the active snapshot window rather than being visible in its older version.
- The API returns a cursor token instead of page numbers. That is the right tradeoff for fast, stable pagination on changing data.
- The seed script uses batched bulk inserts rather than row-by-row inserts so loading 200,000 rows stays practical.

## Local run

1. Create a PostgreSQL database.
2. Copy `.env.example` to `.env` and set `DATABASE_URL`.
3. Install dependencies.
4. Run migrations.
5. Seed the database.
6. Start the API.

## Commands

```bash
pip install -e .
alembic upgrade head
python scripts/seed_products.py
uvicorn app.main:app --reload
```

## Deployment

The app is ready for Render with an external Neon PostgreSQL database.

- Build command: `pip install -e .`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variable: `DATABASE_URL`

See [DEPLOYMENT.md](DEPLOYMENT.md) for the exact submission checklist.
