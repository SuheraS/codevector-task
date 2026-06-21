from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models import Product
from app.pagination import CursorState, decode_cursor, encode_cursor
from app.schemas import ProductsPage


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _build_query(category: str | None, cursor_state: CursorState | None, limit: int):
    snapshot = cursor_state.snapshot if cursor_state else _now_utc()

    statement = select(Product).where(Product.updated_at <= snapshot)
    if category:
        statement = statement.where(Product.category == category)

    if cursor_state:
        statement = statement.where(
            or_(
                Product.updated_at < cursor_state.updated_at,
                and_(Product.updated_at == cursor_state.updated_at, Product.id < cursor_state.id),
            )
        )

    statement = statement.order_by(Product.updated_at.desc(), Product.id.desc()).limit(limit + 1)
    return statement, snapshot


def list_products(session: Session, category: str | None, cursor: str | None, limit: int) -> ProductsPage:
    cursor_state = decode_cursor(cursor) if cursor else None
    if cursor_state and cursor_state.category != category:
        raise ValueError("Cursor does not match the requested category filter")

    statement, snapshot = _build_query(category, cursor_state, limit)
    items = session.execute(statement).scalars().all()

    has_more = len(items) > limit
    page_items = items[:limit]
    next_cursor = None
    if has_more and page_items:
        last_item = page_items[-1]
        next_cursor = encode_cursor(
            CursorState(
                snapshot=snapshot,
                updated_at=last_item.updated_at,
                id=last_item.id,
                category=category,
            )
        )

    return ProductsPage(items=page_items, next_cursor=next_cursor, snapshot=snapshot, has_more=has_more)
