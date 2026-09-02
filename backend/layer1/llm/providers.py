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
                    "model": "llama-3.1-70b-versatile",
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
    """Proveedor de fallback basado en reglas"""
    
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
        """Genera interpretación basada en reglas económicas."""
        return self._generate_fallback(user_prompt)
    
    def _generate_fallback(self, user_prompt: str) -> str:
        """Genera interpretación económica determinista."""
        import re
        
        # Extraer información del prompt
        direction_match = re.search(r'direction[:"]*\s*([A-Z_]+)', user_prompt)
        direction = direction_match.group(1) if direction_match else "UNKNOWN"
        
        prob_match = re.search(r'probability[:"]*\s*([\d.]+)', user_prompt)
        probability = float(prob_match.group(1)) if prob_match else 0.5
        
        edge_match = re.search(r'edge_ratio[:"]*\s*([\d.]+)', user_prompt)
        edge = float(edge_match.group(1)) if edge_match else 0
        
        min_edge_match = re.search(r'minimum_edge[:"]*\s*([\d.]+)', user_prompt)
        min_edge = float(min_edge_match.group(1)) if min_edge_match else 1.5
        
        actionable = edge >= min_edge
        
        direction_es = "alcista" if direction == "UP" else "bajista"
        
        bullets = [
            f"El modelo mantiene un sesgo {direction_es} para USD/JPY con una probabilidad del {probability:.0f}%.",
        ]
        
        if actionable:
            bullets.append(
                f"El edge económico de {edge:.1f}x supera el mínimo requerido de {min_edge:.1f}x, "
                f"haciendo que la señal sea económicamente accionable."
            )
        else:
            bullets.append(
                f"El edge económico de {edge:.1f}x no alcanza el mínimo requerido de {min_edge:.1f}x, "
                f"por lo que la señal no es accionable actualmente."
            )
        
        bullets.append(
            "El entorno de riesgo actual es consistente con la dirección de la señal."
        )
        
        bullets.append(
            "MeridianFX recomienda monitorear la evolución del edge y las condiciones macro."
        )
        
        return "\n".join([f"• {b}" for b in bullets])
