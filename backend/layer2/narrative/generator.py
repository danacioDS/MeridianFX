"""
Narrative generator — calls the LLM (Groq) with automatic fallback.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

from backend.layer1.llm.manager import LLMFallbackManager

from .prompt_builder import (
    build_system_prompt,
    build_user_prompt,
    build_fallback_narrative,
)

logger = logging.getLogger(__name__)


class NarrativeGenerator:
    """Generate narratives via LLM with deterministic fallback."""

    def __init__(self):
        self._llm = LLMFallbackManager()

    async def generate(
        self,
        decision_result: Dict[str, Any],
    ) -> Tuple[str, str, str]:
        """Returns: (narrative_text, provider, model)."""
        try:
            system_prompt = build_system_prompt()
            user_prompt = build_user_prompt(decision_result)

            result = await self._llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=700,
            )

            text = (result.get("text") or "").strip()
            provider = result.get("provider", "unknown")

            if not text or provider == "FallbackLLM":
                logger.info("LLM returned fallback; using deterministic template")
                return (
                    build_fallback_narrative(decision_result),
                    "deterministic-fallback",
                    "template-v1",
                )

            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            narrative = "\n\n".join(paragraphs)

            return (narrative, provider, self._model_name(provider))

        except Exception as exc:
            logger.warning(f"Narrative generation failed: {exc}")
            return (
                build_fallback_narrative(decision_result),
                "deterministic-fallback",
                "template-v1",
            )

    @staticmethod
    def _model_name(provider: str) -> str:
        if provider == "groq":
            return "qwen/qwen3.8-27b"
        return provider
