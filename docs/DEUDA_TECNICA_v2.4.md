# Deuda técnica — v2.4

**Última actualización**: 11 de septiembre de 2026 (cierre Sprint 8)

Este documento acumula bugs y deudas descubiertas durante el desarrollo de v2.4.
Se revisa al cerrar cada sprint.

---

## Sprint 8 — Resumen

Todos los items de Sprint 8 han sido **resueltos, descartados o diferidos**.

| ID | Item | Estado | Commit |
|----|------|--------|--------|
| B1 | probability idéntica en 30/60/90d | ✅ No es bug (propiedad del modelo) | — |
| B2 | expected_return escala lineal ×2/×3 | ✅ Resuelto (√t) | b89c55b |
| B3 | expected_return mostrado como % (es bps) | ✅ Resuelto (÷100) | b89c55b |
| B4 | NBS API 403 | ✅ No es bug (WARNING correcto) | — |
| B5 | Typos en strings backend | ✅ No reproducido (falso positivo) | — |
| F1 | useForecastDashboard sin tipos | ✅ Resuelto | 904a3e5 + pendiente |
| F2 | TabNav sin consumidor | ✅ Eliminado | 5bd324e |
| F3 | Páginas legacy (7 archivos) | ✅ Eliminadas | 5bd324e |
| F4 | NotAvailable con strings técnicos | 🟡 Diferido a v2.5 | — |
| F5 | Backups .pre-* residuales | ✅ Eliminados | 9e5edee |
| A1 | confidence_interval escala rota | ✅ Resuelto (÷10000 espurio) | 904a3e5 |

---

## Backend

### B1 — probability idéntica en 30/60/90d ✅ NO ES BUG

**Estado**: Propiedad del modelo actual.

El motor `Logistic_24` calcula la probabilidad de dirección una sola vez,
independiente del horizonte. El `forecast_dashboard.py` ya pasa
`horizon_days` al engine (fix b89c55b), pero el modelo sigue devolviendo
el mismo valor para los 3 horizontes.

No es un bug introducido por el dashboard. Es una simplificación del
modelo. Multi-horizonte real requeriría entrenar 3 modelos distintos.

---

### B2 — expected_return escala lineal ×2/×3 ✅ RESUELTO

**Commit**: b89c55b

**Causa**: `forecast_dashboard.py:60` llamaba a `engine.get_forecast(pair)`
sin el `horizon_days`, y luego extrapolaba linealmente con
`* (horizon_days / 30)`.

**Fix**: pasar `horizon_days` al engine y eliminar la extrapolación.
El engine ya calcula con `√(horizon_days/365)`.

**Efecto**:
- 30d: -0.73%  (igual)
- 60d: -1.04%  (era -1.47%)
- 90d: -1.27%  (era -2.21%)

---

### B3 — expected_return mostrado como % (es bps) ✅ RESUELTO

**Commit**: b89c55b

**Causa**: `/v1/canonical/{pair}/decision` devuelve `expected_return` en
**bps** (`economic.py:36`), pero `DecisionMetrics.tsx` lo mostraba como %.

**Fix**: dividir por 100 antes de mostrar.
- Antes: -73.25%
- Después: -0.73%

---

### B4 — NBS API 403 ✅ NO ES BUG

**Estado**: Comportamiento correcto.

El provider `CNBSProvider` intenta conectar a `data.stats.gov.cn`. Cuando
la API devuelve 403, el código ya lo maneja con `logger.warning` (nivel
apropiado para un 403 esperado). El backend marca el provider como
`available=False` y la cadena prueba con World Bank e Investing.com.

No hay acción requerida.

---

### B5 — Typos en strings backend ✅ NO REPRODUCIDO

**Estado**: Falso positivo.

Las verificaciones sobre `/v1/market-intelligence` y el código fuente
confirman que los strings se generan correctamente. El aparente
"selectivityover" era un artefacto de truncado en el análisis manual.

---

### A1 — confidence_interval escala rota ✅ RESUELTO

**Commit**: 904a3e5

**Causa**: `decision_engine_adapter.py:94` dividía `expected_volatility`
por 10000, pero el valor ya estaba en decimal.

**Efecto**:
- Antes: ancho = 3.7e-06 (microscópico)
- Después: ancho = 0.0374 (realista)

**Ejemplos**:
- GBP/USD: ci=[0.138, 0.176]
- USD/JPY: ci=[0.339, 0.439]
- USD/BOB: ci=[0.918, 1.000]

---

## Frontend

### F1 — useForecastDashboard sin tipos ✅ RESUELTO

**Commit**: 904a3e5 (pendiente)

Se añadieron tipos completos derivados del contrato real del endpoint:
- DashboardSpot
- DashboardTrend
- DashboardForecast
- DashboardForecastModel
- DashboardHistoryPoint
- ForecastDashboard

---

### F2 — TabNav sin consumidor ✅ ELIMINADO

**Commit**: 5bd324e

`src/components/common/TabNav.tsx` (45 líneas) eliminado. Export removido
del barrel.

---

### F3 — Páginas legacy ✅ ELIMINADAS

**Commit**: 5bd324e

Eliminadas 7 páginas y sus rutas:
- ForecastPageCanonical.tsx
- DriversPage.tsx
- EvaluationPage.tsx
- StatusPage.tsx
- PricePage.tsx
- ModelComparisonPage.tsx
- ForecastPage.tsx

**Impacto en bundle**: -21 módulos, -68 KB (-10 KB gzip).

---

### F4 — NotAvailable con strings técnicos 🟡 DIFERIDO A v2.5

**Estado**: Aplazado.

Con la eliminación de las páginas legacy (F3), la mayoría de los 16 usos
de `NotAvailable` quedaron huérfanos (drivers/*, evaluation/*, status/*,
forecast/*). Solo `RegimeBar.tsx` (en `/macro`) sigue siendo visible.

**Acción v2.5**:
1. Eliminar componentes huérfanos
2. Rediseñar `NotAvailable` para RegimeBar
3. Considerar si los strings técnicos (`NO_FALLBACK_ALLOWED`, etc.)
   deben permanecer visibles o colapsarse en un `<details>`

---

### F5 — Backups .pre-* residuales ✅ ELIMINADOS

**Commit**: 9e5edee

Todos los backups del Sprint 8 eliminados:
- backend/layer1/routers/forecast_dashboard.py.pre-sprint8
- backend/layer2/decision/filter.py.pre-sprint8
- backend/layer2/engine.py.pre-sprint8
- frontend/src/components/decision/DecisionMetrics.tsx.pre-sprint8
- frontend/src/App.tsx.pre-sprint8-fix

---

## Historial de cierres

| Sprint   | Fecha       | Deudas resueltas                                       |
|----------|-------------|--------------------------------------------------------|
| Sprint 6 | 10-sep-2026 | Fuentes, refactor RankingTable, fix snapshot_timestamp |
| Sprint 7 | 11-sep-2026 | Contract alignment, React Router, fuentes, empty states|
| Sprint 8 | 11-sep-2026 | B1-B5, F1-F5, confidence_interval                      |

---

## Prioridad para v2.5

**Alta**:
1. F4 (NotAvailable rediseño + limpieza de componentes huérfanos)

**Media**:
2. Modelo multi-horizonte (B1 real)
3. Migrar todos los hooks a tipos completos

**Baja**:
4. Limpieza de tipos locales en MarketPage
5. Rediseño de `/status` si se re-añade

---

## Estado de v2.4

**Cerrado**: todos los items de Sprint 8 resueltos o descartados (salvo F4
diferido). Listo para tag v2.4.
