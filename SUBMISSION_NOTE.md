# Submission Note

I chose FastAPI, SQLAlchemy, PostgreSQL, Alembic, and Render because they keep the solution small, easy to explain, and practical to deploy with a free Neon database.

## Why this approach

I used keyset pagination instead of OFFSET because the task explicitly required fast pagination and stable results while data changes. The cursor is built from `updated_at DESC` and `id DESC`, and it also carries a snapshot timestamp so browsing stays consistent even when new rows are inserted or updated.

The seed script inserts 200,000 rows in batches instead of row-by-row inserts so loading the dataset stays efficient.

## What I would improve with more time

- Add a proper integration test suite against PostgreSQL, not just SQLite-backed pagination checks.
- Add request logging and structured observability for production debugging.
- Add a small admin endpoint or background job for controlled product updates.
- Expand the UI with back-navigation history persisted in the URL.

## How I used AI

AI helped with the initial scaffold, migration boilerplate, UI generation, and writing the first pass of the README and submission note.

I caught and fixed a few things manually:

- an eager database engine initialization that would have made imports brittle
- test discovery mismatch between pytest-style tests and unittest execution
- the seed script initially building all 200,000 rows in memory before batching

The final code was verified locally with editable install, unit tests, and import smoke checks.
