"""
Narrative service — orchestrates cache lookup, generation, and persistence.

Cache strategy:
    1. Compute narrative_key (stable identity).
    2. Look up (pair, horizon, key, prompt_version).
    3. If HIT → increment served_count, return.
    4. If MISS → call LLM (or fallback), persist, return.
    5. NO TTL. Invalidation happens only when the decision changes.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from .prompt_builder import compute_narrative_key, PROMPT_VERSION
from .repository import NarrativeRepository
from .generator import NarrativeGenerator

logger = logging.getLogger(__name__)


class NarrativeService:
    def __init__(
        self,
        repository: NarrativeRepository,
        generator: NarrativeGenerator,
    ):
        self.repo = repository
        self.generator = generator

    async def get_or_generate(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        pair = decision_result.get("pair") or (decision_result.get("decision") or {}).get("pair")
        horizon_days = (
            decision_result.get("horizon_days")
            or (decision_result.get("decision") or {}).get("horizon_days", 30)
        )

        if not pair:
            raise ValueError("decision_result must contain 'pair'")

        narrative_key = compute_narrative_key(decision_result)

        # 1. Cache lookup
        cached = await self.repo.get(
            pair=pair,
            horizon_days=horizon_days,
            narrative_key=narrative_key,
            prompt_version=PROMPT_VERSION,
        )

        if cached:
            await self.repo.increment_served(cached["id"])
            return {
                "pair": pair,
                "horizon_days": horizon_days,
                "narrative_key": narrative_key,
                "prompt_version": PROMPT_VERSION,
                "narrative": cached["narrative"],
                "provider": cached["provider"],
                "model": cached["model"],
                "generated_at": cached["generated_at"],
                "last_served_at": cached["last_served_at"],
                "generation_count": cached["generation_count"],
                "served_count": cached["served_count"] + 1,
                "cache": {"hit": True},
            }

        # 2. Cache miss → generate
        logger.info(f"Narrative cache MISS: {pair} {horizon_days}d key={narrative_key}")
        narrative, provider, model = await self.generator.generate(decision_result)

        # 3. Persist ONLY if the LLM produced it.
        # Deterministic fallback is served temporarily but NOT cached,
        # so the next request retries the LLM.
        if provider == "deterministic-fallback":
            logger.warning(
                f"Narrative fallback used for {pair} {horizon_days}d — NOT persisting"
            )
            return {
                "pair": pair,
                "horizon_days": horizon_days,
                "narrative_key": narrative_key,
                "prompt_version": PROMPT_VERSION,
                "narrative": narrative,
                "provider": provider,
                "model": model,
                "generated_at": None,
                "last_served_at": None,
                "generation_count": 0,
                "served_count": 1,
                "cache": {"hit": False, "persisted": False},
            }

        saved = await self.repo.create(
            pair=pair,
            horizon_days=horizon_days,
            narrative_key=narrative_key,
            prompt_version=PROMPT_VERSION,
            narrative=narrative,
            provider=provider,
            model=model,
        )

        return {
            "pair": pair,
            "horizon_days": horizon_days,
            "narrative_key": narrative_key,
            "prompt_version": PROMPT_VERSION,
            "narrative": narrative,
            "provider": provider,
            "model": model,
            "generated_at": saved.get("generated_at"),
            "last_served_at": saved.get("last_served_at"),
            "generation_count": saved.get("generation_count", 1),
            "served_count": saved.get("served_count", 1),
            "cache": {"hit": False, "persisted": True},
        }
