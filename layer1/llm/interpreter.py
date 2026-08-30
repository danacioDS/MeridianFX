"""
Economic Interpreter — Genera interpretación económica usando LLM.
"""

import json
import re
from typing import List, Dict
from .manager import LLMFallbackManager


class EconomicInterpreter:
    """
    Interpreta el Decision Context económicamente.
    """
    
    def __init__(self):
        self.llm = LLMFallbackManager()
    
    def build_prompt(self, context: dict) -> tuple[str, str]:
        """Construye los prompts para el LLM."""
        direction = context.get("direction", "UNKNOWN")
        probability = context.get("probability", 0.5)
        economic_filter = context.get("economic_filter", {})
        regime = context.get("regime", "UNKNOWN")
        pair = context.get("pair", "USD/JPY")
        
        direction_es = "alcista" if direction == "UP" else "bajista"
        direction_em = "▲" if direction == "UP" else "▼"
        actionable = economic_filter.get("actionable", False)
        edge = economic_filter.get("edge_ratio", 0)
        min_edge = economic_filter.get("minimum_edge", 1.5)
        gross_return = economic_filter.get("gross_return", 0)
        net_return = economic_filter.get("net_return", 0)
        spread = economic_filter.get("spread_cost", 0)
        slippage = economic_filter.get("slippage_cost", 0)
        fees = economic_filter.get("fees", 0)
        
        system_prompt = """Eres la Capa de Interpretación Económica de MeridianFX.

Tu rol es explicar el significado económico de una decisión cuantitativa
ya producida por MeridianFX.

REGLAS ESTRICTAS:
- Usa SOLO los datos proporcionados en el contexto.
- No inventes datos económicos.
- No repitas números mecánicamente.
- Explica el SIGNIFICADO ECONÓMICO.

Devuelve exactamente 3-4 bullets económicos concisos."""
        
        user_prompt = f"""Contexto de decisión para {pair}:

DATOS REALES:
- Dirección: {direction_em} {direction_es}
- Probabilidad: {probability*100:.1f}%
- Retorno Bruto: {gross_return*100:.4f}%
- Costos: Spread {spread*100:.4f}% + Slippage {slippage*100:.4f}% + Fees {fees*100:.4f}%
- Retorno Neto: {net_return*100:.4f}%
- Edge Ratio: {edge:.4f}x
- Edge Mínimo: {min_edge:.1f}x
- Accionable: {"SÍ" if actionable else "NO"}

CONTEXTO MACRO:
- Régimen: {regime}
- VIX: {context.get('vix', 0):.1f}
- Diferencial de Rendimientos: {context.get('yield_spread', 0):.2f}%
- Divergencia de Política: {context.get('policy_divergence', 'UNKNOWN')}

VALIDEZ:
- Tesis válida: {"SÍ" if context.get('signal_validity', {}).get('thesis_valid', False) else "NO"}
- Condiciones: {', '.join(context.get('signal_validity', {}).get('thesis_conditions', ['No especificadas']))}

Genera 3-4 bullets económicos explicando POR QUÉ esta señal es relevante AHORA.
Cada bullet debe explicar el significado económico, no solo repetir números."""
        
        return system_prompt, user_prompt
    
    async def interpret(self, context: dict) -> List[str]:
        """Interpreta el Decision Context usando LLM con fallback."""
        try:
            system_prompt, user_prompt = self.build_prompt(context)
            result = await self.llm.generate(system_prompt, user_prompt)
            
            if result.get("provider") == "FallbackLLM":
                return self._fallback_interpretation(context)
            
            text = result.get("text", "")
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            
            bullets = []
            for line in lines:
                if line.startswith(("-", "•", "1.", "2.", "3.", "4.")):
                    clean = line.lstrip("-• 0123456789.").strip()
                    if clean:
                        bullets.append(clean)
            
            if not bullets:
                return self._fallback_interpretation(context)
            
            return bullets[:4]
            
        except Exception as e:
            print(f"⚠️ LLM interpret error: {e}")
            return self._fallback_interpretation(context)
    
    def _fallback_interpretation(self, context: dict) -> List[str]:
        """Interpretación de fallback usando los datos reales del contexto."""
        # Extraer datos reales del contexto
        direction = context.get("direction", "UNKNOWN")
        probability = context.get("probability", 0.5)
        pair = context.get("pair", "USD/JPY")
        
        economic_filter = context.get("economic_filter", {})
        regime = context.get("regime", "UNKNOWN")
        yield_spread = context.get("yield_spread", 0)
        vix = context.get("vix", 0)
        policy_divergence = context.get("policy_divergence", "UNKNOWN")
        signal_validity = context.get("signal_validity", {})
        previous = context.get("previous", {})
        
        direction_es = "alcista" if direction == "UP" else "bajista"
        actionable = economic_filter.get("actionable", False)
        edge = economic_filter.get("edge_ratio", 0)
        min_edge = economic_filter.get("minimum_edge", 1.5)
        net_return = economic_filter.get("net_return", 0)
        gross_return = economic_filter.get("gross_return", 0)
        
        bullets = []
        
        # 1. Dirección y probabilidad
        if probability > 0:
            bullets.append(
                f"El modelo mantiene un sesgo {direction_es} para {pair} "
                f"con una probabilidad del {probability*100:.1f}%."
            )
        else:
            bullets.append(f"El modelo mantiene un sesgo {direction_es} para {pair}.")
        
        # 2. Edge y acción
        if actionable:
            bullets.append(
                f"El edge económico de {edge:.2f}x supera el mínimo requerido de {min_edge:.1f}x, "
                f"haciendo que la señal sea accionable."
            )
        else:
            if edge > 0:
                bullets.append(
                    f"El edge económico de {edge:.3f}x no alcanza el mínimo requerido de {min_edge:.1f}x, "
                    f"por lo que la señal no es accionable actualmente."
                )
            else:
                bullets.append(
                    f"El retorno esperado es demasiado reducido ({gross_return*100:.4f}%) "
                    f"para compensar los costos de ejecución, por lo que la señal no es accionable."
                )
        
        # 3. Régimen
        if regime == "RISK_ON":
            bullets.append(
                "El régimen Risk-On es favorable para la tesis, "
                "reduciendo la presión sobre posiciones direccionales."
            )
        elif regime == "RISK_OFF":
            bullets.append(
                "El régimen Risk-Off introduce cautela, "
                "limitando la exposición a posiciones direccionales."
            )
        else:
            bullets.append(
                "El entorno de riesgo actual es consistente con la dirección de la señal."
            )
        
        # 4. Diferencial de rendimientos
        if yield_spread and yield_spread > 2.5:
            bullets.append(
                f"El diferencial de rendimientos se mantiene en {yield_spread:.2f}%, "
                f"proporcionando soporte macro a la tesis."
            )
        elif yield_spread and yield_spread > 0:
            bullets.append(
                f"El diferencial de rendimientos de {yield_spread:.2f}% "
                f"es un factor a considerar en la evaluación de la señal."
            )
        else:
            bullets.append(
                "MeridianFX recomienda monitorear la evolución del edge y las condiciones macro."
            )
        
        return bullets[:4]
