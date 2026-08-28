#!/usr/bin/env python
"""
Script de prueba para el servicio macro.
"""

import asyncio
import json
from layer2.data.macro.service import MacroService


async def test_macro():
    print("🧪 Probando Macro Service...")
    
    service = MacroService()
    
    # Obtener contexto macro
    print("\n📊 Obteniendo contexto macro...")
    context = await service.get_macro_context()
    
    print("\n📋 Resumen Macro:")
    print(json.dumps(context.get("summary", {}), indent=2))
    
    print("\n📊 Indicadores:")
    print(json.dumps(context.get("indicators", {}), indent=2))
    
    print("\n📈 Relevancia FX:", context.get("fx_relevance"))
    
    print("\n💾 Estado de caché:")
    print(json.dumps(service.get_cache_status(), indent=2))


if __name__ == "__main__":
    asyncio.run(test_macro())
