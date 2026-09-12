"""
Narrative router — persistent LLM-generated explanations for canonical decisions.

Endpoints:
    GET  /v1/canonical/{pair}/narrative            → cache-first narrative
    POST /v1/canonical/{pair}/narrative/regenerate → force regeneration (admin)
"""
from __future__ import annotations

import os

from fastapi import APIRouter, Header, HTTPException

from backend.layer1.routers.canonical import bridge
from backend.layer2.narrative.repository import SqliteNarrativeRepository
from backend.layer2.narrative.generator import NarrativeGenerator
from backend.layer2.narrative.service import NarrativeService


router = APIRouter(tags=["narrative"])

# Singletons for the narrative layer
_repository = SqliteNarrativeRepository()
_generator = NarrativeGenerator()
_service = NarrativeService(_repository, _generator)


@router.get("/{pair:path}/narrative")
async def get_canonical_narrative(pair: str, horizon_days: int = 30):
    """
    Return the narrative for the given decision.

    Cache-first: only the first call for a given (pair, horizon, decision state)
    triggers an LLM call. Subsequent calls are served from persistent storage.
    """
    try:
        decision_result = await bridge.evaluate_pair(pair, horizon_days)
        if "error" in decision_result:
            raise HTTPException(status_code=404, detail=decision_result["error"])
        return await _service.get_or_generate(decision_result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{pair:path}/narrative/regenerate")
async def regenerate_canonical_narrative(
    pair: str,
    horizon_days: int = 30,
    x_admin_token: str = Header(default=""),
):
    """
    Force regeneration of the narrative (admin only).
    Requires header: X-Admin-Token: <ADMIN_TOKEN>
    """
    expected = os.getenv("ADMIN_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Admin token not configured")
    if x_admin_token != expected:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        decision_result = await bridge.evaluate_pair(pair, horizon_days)
        if "error" in decision_result:
            raise HTTPException(status_code=404, detail=decision_result["error"])

        from backend.layer2.narrative.prompt_builder import (
            compute_narrative_key,
            PROMPT_VERSION,
        )

        narrative_key = compute_narrative_key(decision_result)
        narrative, provider, model = await _generator.generate(decision_result)

        saved = await _repository.upsert(
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
            "narrative": narrative,
            "provider": provider,
            "model": model,
            "regenerated": True,
            "saved": saved,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
