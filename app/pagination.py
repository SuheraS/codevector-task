from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CursorState:
    snapshot: datetime
    updated_at: datetime
    id: int
    category: str | None


def _encode_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _decode_datetime(value: str) -> datetime:
    decoded = datetime.fromisoformat(value)
    if decoded.tzinfo is None:
        return decoded.replace(tzinfo=timezone.utc)
    return decoded.astimezone(timezone.utc)


def encode_cursor(state: CursorState) -> str:
    payload = {
        "snapshot": _encode_datetime(state.snapshot),
        "updated_at": _encode_datetime(state.updated_at),
        "id": state.id,
        "category": state.category,
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(token: str) -> CursorState:
    padding = "=" * (-len(token) % 4)
    raw = base64.urlsafe_b64decode((token + padding).encode("ascii"))
    payload = json.loads(raw.decode("utf-8"))
    return CursorState(
        snapshot=_decode_datetime(payload["snapshot"]),
        updated_at=_decode_datetime(payload["updated_at"]),
        id=int(payload["id"]),
        category=payload.get("category"),
    )
