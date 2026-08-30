# MERIDIAN FX — RESULTADOS DE INVESTIGACIÓN

## Fecha: 2026-08-30

---

## 1. RESUMEN EJECUTIVO

Meridian FX es un sistema de inteligencia financiera para FX que implementa:

- **Layer 1**: FastAPI Delivery API
- **Layer 2**: Decision Engine con XGBoost, SHAP, FRED
- **Layer 3**: Research Layer con walk-forward, Research Gate
- **Layer 4**: Data Layer con PIT validation
- **Frontend**: React + TypeScript (55 tests, build OK)

---

## 2. RESULTADOS DEL RESEARCH GATE

### Modelo: XGBoost v1.0 (USD/JPY)

| Métrica | Valor | Umbral | Resultado |
|---------|-------|--------|-----------|
| DA | 52.38% | > 52% | ✅ PASA |
| AUC | 55.37% | > 55% | ✅ PASA |
| Sharpe | -0.040 | > 0.3 | ❌ FALLA |
| PF | 0.985 | > 1.2 | ❌ FALLA |

### Decisión: ❌ REJECTED

---

## 3. BENCHMARKS REALES

| Estrategia | Sharpe | PF | Return |
|------------|--------|----|--------|
| **Model** | **-0.040** | **0.985** | **-1.1%** |
| Always Long | 0.557 | 1.228 | +16.3% |
| Always Short | -0.557 | 0.814 | -14.0% |
| Random 50/50 | -0.210 | 0.925 | -5.5% |

### Conclusión
El modelo NO supera a Always Long en el período OOS evaluado.

---

## 4. ANÁLISIS POR VENTANA

| Ventana | Período | Sharpe | PF | Observación |
|---------|---------|--------|----|-------------|
| W1 | 2023-2024 | -0.452 | 0.848 | ❌ Mala |
| W2 | 2024-2025 | 1.245 | 1.529 | ✅ Buena |
| W3 | 2025-2026 | 1.035 | 1.458 | ✅ Buena |

### Observación
El modelo mejora con más datos de entrenamiento (efecto expanding window).

---

## 5. ARQUITECTURA VALIDADA

✅ **PIT-1 a PIT-7**: Todas las invariantes temporales validadas
✅ **Research Gate**: Funcional, rechaza modelos que no cumplen umbrales
✅ **Walk-Forward**: Implementado con expanding window
✅ **Benchmarks**: Comparación cuantitativa con estrategias triviales
✅ **Layer 3**: Research Layer implementada
✅ **Layer 4**: Data Layer implementada

---

## 6. PRÓXIMOS PASOS

| Prioridad | Acción | Descripción |
|-----------|--------|-------------|
| 1 | **Aumentar datos** | Probar con 5 años de entrenamiento inicial |
| 2 | **Ensemble (E7)** | Combinar XGBoost + Logistic + ARIMA |
| 3 | **Decision Policy** | Probar thresholds de probabilidad |
| 4 | **Despliegue** | Render + Neon PostgreSQL |

---

## 7. CONCLUSIÓN

Meridian FX es un sistema completo y funcional con:
- Arquitectura por capas validada
- Research Gate operativo
- Walk-forward y benchmarks implementados

El modelo XGBoost v1.0 fue rechazado por el Research Gate, pero el sistema está listo para:
- Probar nuevas arquitecturas de modelos
- Ajustar políticas de decisión
- Desplegar en producción

---

**Status:** 🟡 EN DESARROLLO
**Siguiente:** Ensamble E7 + Decision Policy
