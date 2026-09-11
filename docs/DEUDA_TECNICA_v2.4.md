# Deuda técnica — v2.4

**Última actualización**: 11 de septiembre de 2026

---

## Backend (congelado en v2.3)

### B1 — probability idéntica en 30/60/90d

**Síntoma**: `/v1/fx/{pair}/forecast-dashboard` devuelve el mismo `probability` para los 3 horizontes.

**Evidencia**:
- USD/BOB:  prob=0.99678702 (30d = 60d = 90d)
- GBP/USD:  prob=0.15773466 (30d = 60d = 90d)
- USD/JPY:  prob=0.38723223 (30d = 60d = 90d)
- EUR/USD:  prob=0.00002009 (30d = 60d = 90d)

**Causa probable**: el modelo solo predice a 30d.

**Fix objetivo**: Sprint 8.

### B2 — expected_return escala lineal x2 / x3

**Síntoma**: `expected_return` a 60d = 30d x 2; a 90d = 30d x 3.

**Evidencia**:
- USD/BOB:  4.59  -> 9.18  -> 13.77
- GBP/USD: -0.74  -> -1.47 -> -2.21
- USD/JPY: -0.65  -> -1.30 -> -1.95
- EUR/USD: -1.15  -> -2.30 -> -3.46

**Causa probable**: extrapolación lineal desde 30d.

**Fix objetivo**: Sprint 8.

---

### B3 — artifact.expected_return absurdos en /decision

**Síntoma**: valores imposibles para FX a 30 días.
- GBP/USD: -71.00%
- USD/JPY: -65.40%
- EUR/USD: -116.96%
- USD/BOB: +455.59%

**Causa probable**: `volatility` en bps, no en fracción (engine.py:346).

**Signo inconsistente** entre artifact/economic/decision.

**Fix objetivo**: Sprint 8.

### B4 — NBS API 403

**Síntoma**: "NBS API error: 403" en el log al calcular CNY.

**Impacto**: cosmético. No bloqueante.

**Fix objetivo**: Sprint 8.

---

### B5 — Typos en strings del backend

- "actionablecuando"     -> "actionable cuando"
- "no es suficientesi"   -> "no es suficiente si"
- "Monitoredopportunity" -> "Monitored opportunity"
- "thereforefavors"      -> "therefore favors"

**Fix objetivo**: Sprint 8.

---

## Frontend

### F1 — useForecastDashboard sin tipos

**Síntoma**: el hook devuelve `any`. El shape no se valida.

**Fix objetivo**: Sprint 8.

### F2 — TabNav.tsx sin consumidor

**Síntoma**: existe pero no se usa.

**Fix objetivo**: Sprint 8.

### F3 — Páginas legacy

7 páginas accesibles por URL sin link en menú:
- ForecastPageCanonical, DriversPage, EvaluationPage, StatusPage,
  PricePage, ModelComparisonPage, ForecastPage

**Fix objetivo**: Sprint 8 (eliminar).

### F4 — NotAvailable con strings técnicos

**Síntoma**: expone conceptos internos (UNSUPPORTED_BY_CONTRACT,
NO_FALLBACK_ALLOWED) al usuario.

**Fix objetivo**: Sprint 8.

### F5 — Backups .pre-* residuales

**Fix objetivo**: Sprint 8.

---

## Prioridad Sprint 8

**Alta**: B1, B2, B3
**Media**: F1, B4, B5
**Baja**: F2, F3, F4, F5

**Total estimado**: ~3h.
