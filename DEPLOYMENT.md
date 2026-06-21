# Deployment Checklist

This repository is ready for Render + Neon. Use the steps below to finish the submission.

## 1. Create the Neon database

1. Create a free Neon PostgreSQL project.
2. Copy the Neon connection string.
3. Set it as `DATABASE_URL` in Render.

## 2. Deploy on Render

1. Create a new Render Web Service from this Git repository.
2. Use the `render.yaml` in the repo, or set the following manually:
   - Build command: `pip install -e .`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add the `DATABASE_URL` environment variable in Render.
4. Deploy.

## 3. Run migrations

After the service is connected to Neon, run:

```bash
alembic upgrade head
```

## 4. Seed the database

Run the seed script once:

```bash
python scripts/seed_products.py
```

If you seed locally, point `DATABASE_URL` at your local PostgreSQL instance first.

## 5. Smoke test

Check these URLs:

- `/health`
- `/products`
- `/browse`

## 6. What to send in the submission email

- Live Render URL
- GitHub repository URL
- Short note covering:
  - what you chose and why
  - what you would improve with more time
  - how you used AI and what you corrected manually
