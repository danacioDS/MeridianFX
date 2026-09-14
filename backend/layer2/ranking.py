import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from backend.layer2.pipeline import DecisionPipeline

logger = logging.getLogger(__name__)

CANONICAL_FX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
    "USD/CNY", "USD/MXN", "USD/BRL", "USD/ARS", "USD/BOB"
]

class RankingEngine:
    def __init__(
        self,
        registry_path: Optional[Path] = None,
        pipeline: Optional[DecisionPipeline] = None
    ):
        self.registry_path = registry_path or Path("models/registry.json")
        self.pipeline = pipeline or DecisionPipeline()
        self.registry_data = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load registry from {self.registry_path}: {e}")
        return {"models": []}

    def evaluate_all_pairs(self) -> List[Dict[str, Any]]:
        rankings = []
        registry_models = {
            m["pair"]: m for m in self.registry_data.get("models", [])
        }

        for pair in CANONICAL_FX_PAIRS:
            rankings.append({
                "pair": pair,
                "has_model": pair in registry_models
            })

        return rankings
