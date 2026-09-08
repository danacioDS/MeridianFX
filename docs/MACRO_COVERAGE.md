# Macro Data Coverage - MeridianFX

## Estado Actual (Septiembre 2026)

### Cobertura de Datos Macro

| Indicador | Cobertura | Fuente | Estado |
|-----------|-----------|--------|--------|
| GDP Growth | 10/10 países | World Bank | ✅ |
| Inflation | 10/10 países | World Bank | ✅ |
| Unemployment | 10/10 países | World Bank | ✅ |
| Policy Rate | 1/10 países (USD) | FRED | ⚠️ |

### Pares Soportados

| Par | GDP Growth | Inflation | Policy Rate | Status |
|-----|------------|-----------|-------------|--------|
| USD/CNY | ✅ | ✅ | ⚠️ (solo USD) | PARTIAL |
| EUR/USD | ✅ | ✅ | ⚠️ (solo USD) | PARTIAL |
| GBP/USD | ✅ | ✅ | ⚠️ (solo USD) | PARTIAL |
| USD/JPY | ✅ | ✅ | ⚠️ (solo USD) | PARTIAL |
| USD/CHF | ✅ | ✅ | ⚠️ (solo USD) | PARTIAL |
| USD/MXN | ✅ | ✅ | ⚠️ (solo USD) | PARTIAL |
| USD/BRL | ✅ | ✅ | ⚠️ (solo USD) | PARTIAL |
| USD/ARS | ✅ | ✅ | ⚠️ (solo USD) | PARTIAL |
| USD/BOB | ✅ | ✅ | ⚠️ (solo USD) | PARTIAL |

### Comportamiento del Pipeline

| Estado | Descripción | macro_score | signal_validity |
|--------|-------------|-------------|-----------------|
| FULL | Todos los inputs disponibles | Calculado | VALID/DEGRADED |
| PARTIAL | Faltan inputs requeridos | None | UNAVAILABLE |
| UNAVAILABLE | Sin datos macro | None | UNAVAILABLE |

### Integridad de Datos

1. **No se usan datos simulados** - `allow_simulation=False` para providers reales
2. **No se inventan datos** - `None` no se convierte a `0.0`
3. **No se usan proxies** - Policy rate no se reemplaza con otras tasas
4. **Trazabilidad completa** - `macro_data_status` muestra todos los valores

### Próximo Milestone: Policy Rate Coverage

| Moneda | Fuente | Prioridad |
|--------|--------|-----------|
| EUR | ECB | Alta |
| GBP | BoE | Alta |
| JPY | BoJ | Alta |
| CHF | SNB | Media |
| CNY | PBoC | Media |
| MXN | Banxico | Media |
| BRL | BCB | Media |
| ARS | BCRA | Baja |
| BOB | BCB | Baja |
