from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from itertools import islice

from sqlalchemy import delete, insert, text

from app.db import get_session_factory
from app.models import Product

TOTAL_PRODUCTS = 200_000
BATCH_SIZE = 10_000

CATEGORIES = [
    "electronics",
    "fashion",
    "home",
    "sports",
    "beauty",
    "books",
    "toys",
    "groceries",
]

ADJECTIVES = [
    "Nova",
    "Prime",
    "Silver",
    "Urban",
    "Atlas",
    "Rapid",
    "Bright",
    "Quantum",
]

NOUNS = [
    "Speaker",
    "Bottle",
    "Lamp",
    "Jacket",
    "Tablet",
    "Chair",
    "Watch",
    "Bag",
]


def chunked(iterable, size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, size)):
        yield batch


def iter_rows():
    base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    for product_id in range(1, TOTAL_PRODUCTS + 1):
        created_at = base_time + timedelta(minutes=product_id)
        updated_at = created_at + timedelta(minutes=product_id % 240)
        category = CATEGORIES[product_id % len(CATEGORIES)]
        name = f"{ADJECTIVES[product_id % len(ADJECTIVES)]} {NOUNS[product_id % len(NOUNS)]} {product_id}"
        price = Decimal("9.99") + Decimal(product_id % 5000) / Decimal("3.5")
        yield {
            "id": product_id,
            "name": name,
            "category": category,
            "price": price.quantize(Decimal("0.01")),
            "created_at": created_at,
            "updated_at": updated_at,
        }


def reset_identity(session) -> None:
    session.execute(
        text("SELECT setval(pg_get_serial_sequence('products', 'id'), COALESCE((SELECT MAX(id) FROM products), 1), true)")
    )


def main() -> None:
    with get_session_factory()() as session:
        session.execute(delete(Product))
        session.commit()

        for batch in chunked(iter_rows(), BATCH_SIZE):
            session.execute(insert(Product), batch)
            session.commit()

        reset_identity(session)
        session.commit()

    print(f"Inserted {TOTAL_PRODUCTS:,} products in {math.ceil(TOTAL_PRODUCTS / BATCH_SIZE)} batches")


if __name__ == "__main__":
    main()
