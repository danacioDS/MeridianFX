from backend.layer2.data.macro.canonical_adapter import CanonicalMacroAdapter


def test_macro_transformer_regime_maps_to_canonical():
    source = {
        "risk": "MODERATE",
        "policy": "NEUTRAL",
        "growth": "WEAK",
        "inflation": "MODERATE",
    }

    result = CanonicalMacroAdapter.to_canonical(source)

    assert result == {
        "risk": "Neutral",
        "policy": "Neutral",
        "growth": "Low",
        "inflation": "Moderate",
    }


def test_unknown_values_are_preserved():
    source = {
        "risk": "UNKNOWN",
        "policy": "UNKNOWN",
        "growth": "UNKNOWN",
        "inflation": "UNKNOWN",
    }

    result = CanonicalMacroAdapter.to_canonical(source)

    assert result == {
        "risk": "UNKNOWN",
        "policy": "UNKNOWN",
        "growth": "UNKNOWN",
        "inflation": "UNKNOWN",
    }


def test_monetary_risk_proxy_is_not_mapped_to_risk_on_off():
    restrictive = {
        "risk": "RESTRICTIVE",
        "policy": "RESTRICTIVE",
        "growth": "WEAK",
        "inflation": "HIGH",
    }

    accommodative = {
        "risk": "ACCOMMODATIVE",
        "policy": "ACCOMMODATIVE",
        "growth": "STRONG",
        "inflation": "LOW",
    }

    assert CanonicalMacroAdapter.to_canonical(restrictive)["risk"] == "UNKNOWN"
    assert CanonicalMacroAdapter.to_canonical(accommodative)["risk"] == "UNKNOWN"
