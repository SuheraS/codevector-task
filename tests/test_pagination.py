from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Product
from app.pagination import CursorState, decode_cursor, encode_cursor
from app.service import list_products


def make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def seed_products(session: Session, count: int = 6) -> None:
    base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    for product_id in range(1, count + 1):
        session.add(
            Product(
                id=product_id,
                name=f"Product {product_id}",
                category="electronics" if product_id % 2 else "books",
                price=Decimal("19.99"),
                created_at=base_time + timedelta(minutes=product_id),
                updated_at=base_time + timedelta(minutes=product_id),
            )
        )
    session.commit()


class PaginationTests(unittest.TestCase):
    def test_cursor_round_trip(self) -> None:
        state = CursorState(
            snapshot=datetime(2025, 1, 2, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 1, 12, tzinfo=timezone.utc),
            id=42,
            category="electronics",
        )

        token = encode_cursor(state)
        decoded = decode_cursor(token)

        self.assertEqual(decoded, state)

    def test_keyset_pagination_is_stable_across_new_writes(self) -> None:
        session = make_session()
        seed_products(session)

        first_page = list_products(session=session, category=None, cursor=None, limit=2)
        self.assertEqual(len(first_page.items), 2)
        self.assertTrue(first_page.has_more)
        self.assertIsNotNone(first_page.next_cursor)

        base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
        session.add(
            Product(
                id=999,
                name="Late Insert",
                category="electronics",
                price=Decimal("29.99"),
                created_at=base_time + timedelta(days=10),
                updated_at=base_time + timedelta(days=10),
            )
        )
        session.commit()

        second_page = list_products(session=session, category=None, cursor=first_page.next_cursor, limit=2)

        first_ids = {item.id for item in first_page.items}
        second_ids = {item.id for item in second_page.items}

        self.assertTrue(first_ids.isdisjoint(second_ids))
        self.assertNotIn(999, second_ids)

    def test_category_cursor_rejects_mismatched_filter(self) -> None:
        session = make_session()
        seed_products(session)

        page = list_products(session=session, category="electronics", cursor=None, limit=2)
        self.assertIsNotNone(page.next_cursor)

        with self.assertRaisesRegex(ValueError, "category filter"):
            list_products(session=session, category="books", cursor=page.next_cursor, limit=2)
