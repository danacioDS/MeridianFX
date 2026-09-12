"""
Narrative layer — persistent LLM-generated explanations for canonical decisions.

Architecture:
    decision_result (from PipelineBridge)
        ↓
    NarrativeService
        ├── NarrativeRepository (SQLite now, Postgres later)
        └── NarrativeGenerator (Groq + deterministic fallback)
        ↓
    narrative (cached by narrative_key)
"""
