"""Layer 2 v3.4.1 §13 / Prompt 10 — DecisionRegistry.

Patch P8:
  * DecisionRegistry stores ``signal_validity`` and ``rejection_reason``.
  * It does NOT store ``delivery_state`` or ``delivery_reason`` — these are
    Layer 1 concerns (delivery policy).
  * DO NOT add fields that belong to other layers.
"""

from __future__ import annotations

from collections import OrderedDict

from ..contracts.decision import Decision

# Explicitly NOT stored here (Layer 1 concerns — Patch P8).
EXCLUDED_LAYER1_FIELDS = ("delivery_state", "delivery_reason", "delivery_warning")


class DecisionRegistry:
    """In-memory registry of Layer 2 decisions (audit trail, §13)."""

    def __init__(self) -> None:
        self._store: OrderedDict[str, Decision] = OrderedDict()

    def store(self, decision: Decision) -> str:
        """Persist a decision; returns its decision_id.

        Raises ValueError if the decision carries Layer 1 delivery fields.
        """
        for field in EXCLUDED_LAYER1_FIELDS:
            if hasattr(decision, field):
                raise ValueError(
                    f"{field} is a Layer 1 concern (Patch P8) — cannot be stored"
                )
        self._store[decision.decision_id] = decision
        return decision.decision_id

    def get(self, decision_id: str) -> Decision | None:
        return self._store.get(decision_id)

    def get_by_prediction(self, prediction_id: str) -> Decision | None:
        for decision in self._store.values():
            if decision.prediction_id == prediction_id:
                return decision
        return None

    def get_by_pair(self, pair: str, limit: int = 100) -> list[Decision]:
        decisions = [d for d in self._store.values() if d.pair == pair]
        return decisions[-limit:] if limit else decisions

    def get_latest(self, pair: str) -> Decision | None:
        decisions = self.get_by_pair(pair)
        return decisions[-1] if decisions else None

    def get_actionable(self, pair: str) -> list[Decision]:
        return [d for d in self.get_by_pair(pair) if d.actionable]

    def __len__(self) -> int:
        return len(self._store)