# Reporte de Selección de Modelo — MeridianFX

## Fecha
8 de septiembre de 2026

## Objetivo

Evaluar de forma temporalmente robusta qué arquitectura presenta mejor desempeño predictivo para MeridianFX:

1. XGBoost + 23 variables técnicas
2. XGBoost + 23 variables técnicas + `policy_diff`
3. Logistic Regression + 23 variables técnicas
4. Logistic Regression + 23 variables técnicas + `policy_diff`

La evaluación utiliza walk-forward validation con información macroeconómica construida Point-in-Time (PIT), evitando el uso de información futura.

## Resultado principal

El mejor candidato identificado fue:

**Logistic Regression + variables técnicas + `policy_diff`**

Resultados:

- AUC medio: **0.6108**
- Desviación estándar: **0.1025**
- AUC mínimo: **0.4765**
- AUC máximo: **0.7657**
- Brier Score: **0.4229**

Frente al XGBoost técnico:

**Δ AUC = +0.0789**

Frente a Logistic Regression solamente técnica:

**Δ AUC = +0.0268**

El resultado debe considerarse una selección de candidato y no una validación definitiva para producción.

## Comparación

| Modelo | AUC medio | Std | Min AUC | Max AUC | Brier |
|---|---:|---:|---:|---:|---:|
| XGBoost + 23 | 0.5319 | 0.0876 | 0.4175 | 0.6238 | 0.3787 |
| XGBoost + 24 | 0.5145 | 0.1250 | 0.3229 | 0.6733 | 0.3299 |
| Logistic + 23 | 0.5839 | 0.0784 | 0.4962 | 0.7390 | 0.4381 |
| **Logistic + 24** | **0.6108** | **0.1025** | **0.4765** | **0.7657** | **0.4229** |

## Conclusión

La evidencia experimental favorece a Logistic Regression con `policy_diff` como candidato para la siguiente etapa de MeridianFX.

Sin embargo, antes de sustituir el modelo actual de producción se debe completar:

1. Equivalencia exacta entre investigación y producción.
2. Validación del esquema de 24 features.
3. Entrenamiento reproducible del artefacto definitivo.
4. Versionado del modelo.
5. Prueba de predicción idéntica entre research y production.
6. Validación temporal adicional.
7. Shadow validation antes de activar el modelo en producción.

Por tanto, la decisión actual es:

> **Seleccionar Logistic Regression + `policy_diff` como candidato de producción, sujeto a validación pre-producción.**

