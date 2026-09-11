# Deuda técnica — v2.5

**Última actualización**: 11 de septiembre de 2026 (cierre v2.5)
**Baseline**: tag v2.5 → 5ec02d5

---

## Estado v2.5

**Baseline estable de ingeniería.**

- 6 de 6 páginas auditadas
- 56/56 tests pasan
- Build verde (1007 módulos)
- Sin componentes huérfanos
- Sin hooks huérfanos (excepto usePolling, helper genérico)
- Contratos consolidados en types/contracts.ts
- Tag v2.5 → 5ec02d5

---

## Resuelto en v2.5

### Frontend

- **F4** — 16 componentes huérfanos eliminados (drivers, evaluation, status, forecast, global)
- **F5** — 8 hooks huérfanos eliminados/movidos (useMacro, useInterpretation + 6 a _unused)
- **F6** — Tipado de hooks: useForecast, usePrice, useRanking
- **F7** — MarketPage usa PriceResponse del contrato
- **3.1** — Economic Breakdown + Hard Gates en /decision
- **3.1b** — ActionableInfo thresholds dinámicos (desde backend, ya no hardcoded)
- **3.2** — Quality Metrics + Signal Fusion en /decision
- **3.5** — /market deduplicación de tipos (4 interfaces locales → hook)
- **3.6** — /macro deduplicación (3 MacroRegime → 1) + eliminar MacroPanel legacy
- **3.7** — /risk eliminar 5 casts innecesarios
- **3.8** — / usar datos canónicos (top_opportunity, total_actionable, total_pairs) + eliminar 3 huérfanos

### Backend (Sprint 8, parte de v2.4/v2.5)

- **B2** — expected_return escala √t (era lineal ×2/×3)
- **B3** — Frontend: dividir expected_return por 100 (bps → %)
- **A1** — confidence_interval: quitar división /10000 espuria

---

## Deuda diferida

### v2.5.1 — Bug fixes menores

| ID | Deuda | Impacto |
|----|-------|---------|
| B4 | NBS API 403 (bajar nivel de log) | 🟢 Cosmético |
| A2 | expected_volatility unidades en adapter | 🟡 Consistencia |
| F4 | NotAvailable strings técnicos | 🟢 UX |

### v2.6 — Deploy + auditoría cuantitativa

| ID | Deuda | Impacto |
|----|-------|---------|
| Deploy | Frontend + Backend en producción | 🔴 Bloqueante para release |
| A3 | policy_diff múltiples rutas | 🟡 Auditoría |
| A4 | async/event loops | 🟡 Auditoría |

### v3.0 — Expansión

| ID | Feature | Impacto |
|----|---------|---------|
| B1 | Modelo multi-horizonte real | 🔴 Feature |
| Backtesting | Evaluación histórica | 🟡 Feature |
| Más pares | Expandir universo FX | 🟡 Feature |

---

## Filosofía v2.5

**Consolidar, no complicar.**

- Sin features artificiales
- Sin mover tipos sin justificación
- Sin "arreglar" lo que no está roto
- Sin duplicar información entre páginas
- Backend congelado (v2.3), solo se consume

---

## Historial

| Versión | Fecha       | Contenido                                             |
|---------|-------------|-------------------------------------------------------|
| v2.3    | 30-ago-2026 | Risk Assessment Engine                                |
| v2.4    | 10-sep-2026 | Frontend v2.4 (6 páginas canónicas)                   |
| v2.5    | 11-sep-2026 | Baseline de ingeniería + auditoría 6/6 páginas        |
