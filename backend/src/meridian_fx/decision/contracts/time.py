"""Timezone helpers enforcing Layer 4 PIT-5 (all timestamps timezone-aware UTC)."""

from __future__ import annotations

from datetime import datetime, timezone


def ensure_utc(value: datetime | None) -> datetime | None:
    """Force timezone-aware UTC; reject naive timestamps (PIT-5)."""
    if value is None:
        return value
    if value.tzinfo is None:
        raise ValueError("naive datetime is a PIT-5 violation — must be timezone-aware")
    if value.tzinfo != timezone.utc:
        return value.astimezone(timezone.utc)
    return value


def utcnow() -> datetime:
    return datetime.now(timezone.utc)