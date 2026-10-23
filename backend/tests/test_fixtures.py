"""Checks that the shared fixtures follow docs/contracts.md, so every module can rely on them."""

import json
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_mock_result_follows_contract() -> None:
    result = json.loads((FIXTURES / "mock_result.json").read_text(encoding="utf-8"))
    assert result["schema_version"] == 1
    assert result["disclaimer"]
    assert result["vitals"]["bp"]["label"] == "experimental"
    assert "error_band_mmhg" in result["vitals"]["bp"]
    for name in ("hr", "rr"):
        vital = result["vitals"][name]
        assert 0.0 <= vital["confidence"] <= 1.0
        assert vital["label"] in {"measured", "estimated", "experimental", "calculated"}
    for metric in result["derived"].values():
        assert metric["formula"]


def test_mock_derived_values_match_formulas() -> None:
    result = json.loads((FIXTURES / "mock_result.json").read_text(encoding="utf-8"))
    p, v = result["profile"], result["vitals"]
    sbp, dbp = v["bp"]["sbp"]["value"], v["bp"]["dbp"]["value"]
    bmi = p["weight_kg"] / (p["height_cm"] / 100) ** 2
    assert abs(result["derived"]["bmi"]["value"] - bmi) < 0.01
    assert abs(result["derived"]["map"]["value"] - (dbp + (sbp - dbp) / 3)) < 0.01
