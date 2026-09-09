"""
SHAP Explainer para modelos de MeridianFX.

Soporta:
- XGBoost / modelos basados en árboles -> TreeExplainer
- LogisticRegression dentro de sklearn Pipeline
  -> LinearExplainer sobre el modelo transformado
"""

import shap
import pandas as pd
import numpy as np
import joblib
import os
import warnings

warnings.filterwarnings("ignore")


class SHAPExplainer:
    def __init__(self, model, feature_names: list, X_background: pd.DataFrame = None):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self.background = None
        self.model_type = None
        self.imputer = None
        self.scaler = None

        if X_background is not None and len(X_background) > 0:
            self.fit(X_background)

    def fit(self, X: pd.DataFrame):
        """Ajusta el explainer según el tipo de modelo."""
        X = X[self.feature_names].copy().astype(float)
        self.background = X.sample(min(100, len(X)), random_state=42)

        try:
            # ============================================================
            # LogisticRegression dentro de sklearn Pipeline
            # ============================================================
            if hasattr(self.model, "named_steps"):
                steps = self.model.named_steps

                self.imputer = steps.get("imputer")
                self.scaler = steps.get("scaler")
                classifier = steps.get("model")

                if classifier is None:
                    raise ValueError(
                        "Pipeline sin step 'model'"
                    )

                X_background = self.background

                if self.imputer is not None:
                    X_background = self.imputer.transform(X_background)

                if self.scaler is not None:
                    X_background = self.scaler.transform(X_background)

                self.explainer = shap.LinearExplainer(
                    classifier,
                    X_background
                )

                self.model_type = "logistic_pipeline"

                print(
                    f"✅ SHAP LinearExplainer ajustado "
                    f"para Logistic Pipeline con "
                    f"{len(self.background)} muestras"
                )
                return

            # ============================================================
            # Modelos de árboles (XGBoost, etc.)
            # ============================================================
            self.explainer = shap.TreeExplainer(
                self.model,
                self.background,
                feature_perturbation="tree_path_dependent"
            )

            self.model_type = "tree"
            print(
                f"✅ SHAP TreeExplainer ajustado "
                f"con {len(self.background)} muestras"
            )

        except Exception as e:
            print(f"⚠️ SHAP fit error: {e}")

            # Fallback para modelos de árboles
            if self.model_type is None:
                try:
                    self.explainer = shap.TreeExplainer(
                        self.model,
                        feature_perturbation="tree_path_dependent"
                    )
                    self.model_type = "tree"
                    print("✅ SHAP TreeExplainer ajustado sin background")
                except Exception as fallback_error:
                    print(
                        f"❌ SHAP fallback error: {fallback_error}"
                    )
                    self.explainer = None

    def explain(self, X: pd.DataFrame) -> dict:
        """Genera explicación SHAP para una muestra."""

        if self.explainer is None:
            return {
                "base_value": 0,
                "base_probability": 0.5,
                "final_probability": 0.5,
                "contributions": [],
                "feature_count": 0,
                "error": "Explainer not initialized"
            }

        X = X[self.feature_names].copy().astype(float)

        try:
            # Para Logistic Pipeline debemos aplicar exactamente
            # las mismas transformaciones que usa el Pipeline.
            X_explain = X

            if self.model_type == "logistic_pipeline":
                if self.imputer is not None:
                    X_explain = self.imputer.transform(X)

                if self.scaler is not None:
                    X_explain = self.scaler.transform(X_explain)

            shap_values = self.explainer.shap_values(X_explain)

            if isinstance(shap_values, list):
                shap_values = shap_values[1]

            shap_values = np.asarray(shap_values)

            if shap_values.ndim == 2:
                shap_values = shap_values[0]

            expected_value = self.explainer.expected_value

            if isinstance(expected_value, (list, np.ndarray)):
                expected_value = np.asarray(expected_value).flatten()[0]

            base_value = float(expected_value)

            contributions = []

            for i, feature in enumerate(self.feature_names):
                val = float(shap_values[i])

                contributions.append({
                    "feature": feature,
                    "contribution": val,
                    "abs_contribution": abs(val)
                })

            contributions.sort(
                key=lambda x: x["abs_contribution"],
                reverse=True
            )

            import math

            total_shap = sum(
                c["contribution"]
                for c in contributions
            )

            final_prob = 1 / (
                1 + math.exp(-(base_value + total_shap))
            )

            return {
                "base_value": base_value,
                "base_probability": 1 / (
                    1 + math.exp(-base_value)
                ),
                "final_probability": final_prob,
                "contributions": contributions[:10],
                "feature_count": len(contributions)
            }

        except Exception as e:
            print(f"⚠️ SHAP error: {e}")

            return {
                "base_value": 0,
                "base_probability": 0.5,
                "final_probability": 0.5,
                "contributions": [],
                "feature_count": 0,
                "error": str(e)
            }

    def save(self, path: str):
        """Guarda el explainer."""
        os.makedirs(os.path.dirname(path), exist_ok=True)

        saved = {
            "explainer": self.explainer,
            "feature_names": self.feature_names,
            "background": self.background,
            "model_type": self.model_type
        }

        joblib.dump(saved, path)
        print(f"✅ SHAP Explainer guardado en {path}")
