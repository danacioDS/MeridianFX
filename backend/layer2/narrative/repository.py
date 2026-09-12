"""
Narrative repository — persistent storage for generated narratives.

Current implementation: SQLite (local file).
Interface designed to migrate to Postgres (Neon) without changes to callers.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Protocol


class NarrativeRepository(Protocol):
    """Protocol for narrative persistence."""

    async def get(
        self,
        pair: str,
        horizon_days: int,
        narrative_key: str,
        prompt_version: str,
    ) -> Optional[dict]: ...

    async def create(
        self,
        pair: str,
        horizon_days: int,
        narrative_key: str,
        prompt_version: str,
        narrative: str,
        provider: str,
        model: str,
    ) -> dict: ...

    async def increment_served(self, row_id: int) -> None: ...

    async def upsert(
        self,
        pair: str,
        horizon_days: int,
        narrative_key: str,
        prompt_version: str,
        narrative: str,
        provider: str,
        model: str,
    ) -> dict: ...


class SqliteNarrativeRepository:
    """SQLite implementation of NarrativeRepository."""

    def __init__(self, db_path: Path = Path("backend/cache/narratives.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS narratives (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair              TEXT NOT NULL,
                    horizon_days      INTEGER NOT NULL,
                    narrative_key     TEXT NOT NULL,
                    prompt_version    TEXT NOT NULL DEFAULT 'v1',
                    narrative         TEXT NOT NULL,
                    provider          TEXT NOT NULL,
                    model             TEXT NOT NULL,
                    generated_at      TEXT NOT NULL,
                    last_served_at    TEXT NOT NULL,
                    generation_count  INTEGER NOT NULL DEFAULT 1,
                    served_count      INTEGER NOT NULL DEFAULT 0,
                    UNIQUE (pair, horizon_days, narrative_key, prompt_version)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_narrative_key ON narratives(narrative_key)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_last_served ON narratives(last_served_at DESC)"
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _row_to_dict(self, row) -> dict:
        return {
            "id": row[0],
            "pair": row[1],
            "horizon_days": row[2],
            "narrative_key": row[3],
            "prompt_version": row[4],
            "narrative": row[5],
            "provider": row[6],
            "model": row[7],
            "generated_at": row[8],
            "last_served_at": row[9],
            "generation_count": row[10],
            "served_count": row[11],
        }

    async def get(
        self,
        pair: str,
        horizon_days: int,
        narrative_key: str,
        prompt_version: str,
    ) -> Optional[dict]:
        self._init_db()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT id, pair, horizon_days, narrative_key, prompt_version,
                       narrative, provider, model, generated_at, last_served_at,
                       generation_count, served_count
                FROM narratives
                WHERE pair = ? AND horizon_days = ?
                  AND narrative_key = ? AND prompt_version = ?
                """,
                (pair, horizon_days, narrative_key, prompt_version),
            ).fetchone()
        return self._row_to_dict(row) if row else None

    async def create(
        self,
        pair: str,
        horizon_days: int,
        narrative_key: str,
        prompt_version: str,
        narrative: str,
        provider: str,
        model: str,
    ) -> dict:
        self._init_db()
        now = self._now()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO narratives
                (pair, horizon_days, narrative_key, prompt_version,
                 narrative, provider, model, generated_at, last_served_at,
                 generation_count, served_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
                """,
                (
                    pair, horizon_days, narrative_key, prompt_version,
                    narrative, provider, model, now, now,
                ),
            )
            _ = cursor.lastrowid
        return await self.get(pair, horizon_days, narrative_key, prompt_version) or {}

    async def increment_served(self, row_id: int) -> None:
        self._init_db()
        now = self._now()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE narratives
                SET served_count = served_count + 1,
                    last_served_at = ?
                WHERE id = ?
                """,
                (now, row_id),
            )

    async def upsert(
        self,
        pair: str,
        horizon_days: int,
        narrative_key: str,
        prompt_version: str,
        narrative: str,
        provider: str,
        model: str,
    ) -> dict:
        self._init_db()
        now = self._now()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO narratives
                (pair, horizon_days, narrative_key, prompt_version,
                 narrative, provider, model, generated_at, last_served_at,
                 generation_count, served_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
                ON CONFLICT(pair, horizon_days, narrative_key, prompt_version)
                DO UPDATE SET
                    narrative = excluded.narrative,
                    provider = excluded.provider,
                    model = excluded.model,
                    generated_at = excluded.generated_at,
                    last_served_at = excluded.last_served_at,
                    generation_count = generation_count + 1
                """,
                (
                    pair, horizon_days, narrative_key, prompt_version,
                    narrative, provider, model, now, now,
                ),
            )
        return await self.get(pair, horizon_days, narrative_key, prompt_version) or {}
