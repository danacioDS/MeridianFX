"""
Base LLM Provider — Interfaz común para todos los proveedores.
"""

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Interfaz base para proveedores LLM"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del proveedor"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 500,
    ) -> str:
        """
        Genera una respuesta del LLM.
        
        Args:
            system_prompt: Prompt del sistema
            user_prompt: Prompt del usuario
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens a generar
            
        Returns:
            Respuesta generada
        """
        pass
