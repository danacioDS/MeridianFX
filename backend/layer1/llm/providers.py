"""
LLM Providers — Implementaciones para diferentes servicios.
"""

import os
import json
import httpx
from typing import Optional
from .base import LLMProvider


class GroqProvider(LLMProvider):
    """Proveedor Groq (LLaMA/Mixtral)"""
    
    @property
    def name(self) -> str:
        return "groq"
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 500,
    ) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "qwen/qwen3.8-27b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            if response.status_code != 200:
                raise Exception(f"Groq API error: {response.status_code}")
            result = response.json()
            return result["choices"][0]["message"]["content"]


class GLMProvider(LLMProvider):
    """Proveedor GLM (Zhipu AI) - fallback"""
    
    @property
    def name(self) -> str:
        return "glm"
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 500,
    ) -> str:
        # Implementación para GLM (Zhipu)
        # Por ahora, simulamos
        raise NotImplementedError("GLM provider not implemented yet")


class GeminiProvider(LLMProvider):
    """Proveedor Gemini (Google) - fallback"""
    
    @property
    def name(self) -> str:
        return "gemini"
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 500,
    ) -> str:
        # Implementación para Gemini
        # Por ahora, simulamos
        raise NotImplementedError("Gemini provider not implemented yet")


class FallbackLLM(LLMProvider):
    """Proveedor de fallback determinista basado en el prompt."""

    @property
    def name(self) -> str:
        return "rule_based"

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 500,
    ) -> str:
        return self._generate_fallback(user_prompt)

    def _generate_fallback(self, user_prompt: str) -> str:
        import re

        pair_match = re.search(
            r"PAIR:\s*([A-Z]{3}/[A-Z]{3})",
            user_prompt,
            re.IGNORECASE,
        )
        pair = pair_match.group(1).upper() if pair_match else "UNKNOWN"

        direction_match = re.search(
            r"Direction:\s*([A-Z_]+)",
            user_prompt,
            re.IGNORECASE,
        )
        direction = direction_match.group(1).upper() if direction_match else "NEUTRAL"

        confidence_match = re.search(
            r"Confidence:\s*([0-9.]+)%",
            user_prompt,
            re.IGNORECASE,
        )
        confidence = float(confidence_match.group(1)) if confidence_match else 0.0

        edge_match = re.search(
            r"Edge ratio:\s*([0-9.]+)",
            user_prompt,
            re.IGNORECASE,
        )
        edge = float(edge_match.group(1)) if edge_match else 0.0

        min_edge_match = re.search(
            r"Required minimum edge:\s*([0-9.]+)",
            user_prompt,
            re.IGNORECASE,
        )
        min_edge = float(min_edge_match.group(1)) if min_edge_match else 0.0

        actionable_match = re.search(
            r"Actionable:\s*(YES|NO)",
            user_prompt,
            re.IGNORECASE,
        )
        actionable = (
            actionable_match.group(1).upper() == "YES"
            if actionable_match
            else False
        )

        direction_label = {
            "LONG": "bullish",
            "SHORT": "bearish",
            "UP": "bullish",
            "DOWN": "bearish",
            "NEUTRAL": "neutral",
        }.get(direction, "neutral")

        action_text = "reaches" if actionable else "does not reach"
        actionable_text = "is" if actionable else "is not"

        return (
            f"• The model maintains a {direction_label} bias for {pair} "
            f"with a confidence level of {confidence:.1f}%.\n"
            f"• The economic edge ratio is {edge:.2f}x and {action_text} "
            f"the required minimum of {min_edge:.2f}x, so the signal "
            f"{actionable_text} currently actionable.\n"
            f"• The current risk environment is consistent with the direction "
            f"of the signal.\n"
            f"• MeridianFX recommends monitoring the evolution of the edge "
            f"and macro conditions."
        )
