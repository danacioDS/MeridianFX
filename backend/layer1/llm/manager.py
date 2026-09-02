"""
LLM Fallback Manager — Gestiona múltiples proveedores con fallback.
"""

import logging
from typing import List, Optional, Dict
from .base import LLMProvider
from .providers import GroqProvider, GLMProvider, GeminiProvider, FallbackLLM

logger = logging.getLogger(__name__)


class LLMFallbackManager:
    """
    Gestiona múltiples proveedores LLM con fallback automático.
    
    Orden de intentos:
    1. Groq (primary)
    2. GLM (fallback 1)
    3. Gemini (fallback 2)
    4. Rule-based (fallback final)
    """
    
    def __init__(self, providers: Optional[List[LLMProvider]] = None):
        if providers is None:
            providers = [
                GroqProvider(),
                GLMProvider(),
                GeminiProvider(),
                FallbackLLM(),
            ]
        self.providers = providers
        self._errors: List[Dict] = []
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 500,
    ) -> Dict[str, str]:
        """
        Genera respuesta usando el primer proveedor disponible.
        
        Returns:
            Dict con:
            - text: Respuesta generada
            - provider: Nombre del proveedor usado
            - fallback: True si se usó fallback
            - errors: Lista de errores anteriores
        """
        self._errors = []
        
        for provider in self.providers:
            try:
                result = await provider.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                
                return {
                    "text": result,
                    "provider": provider.name,
                    "fallback": len(self._errors) > 0,
                    "errors": self._errors,
                }
                
            except NotImplementedError:
                # Si el proveedor no está implementado, continuar
                self._errors.append({
                    "provider": provider.name,
                    "error": "Not implemented"
                })
                continue
                
            except Exception as exc:
                logger.warning(f"LLM provider {provider.name} failed: {exc}")
                self._errors.append({
                    "provider": provider.name,
                    "error": str(exc)
                })
                continue
        
        # Si todos fallaron, el fallback final debería haber funcionado
        # Pero por si acaso
        raise RuntimeError("All LLM providers failed")
    
    def get_status(self) -> Dict[str, bool]:
        """Obtiene el estado de todos los proveedores"""
        return {
            provider.name: True for provider in self.providers
        }
