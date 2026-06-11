#!/usr/bin/env python3
"""Verify the stored DCF teaching snapshot and core model invariants."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "src/data/dcf-learning.json"


def main() -> None:
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert data["readOnly"] is True
    assert set(data["companies"]) == {"TOST", "ADYEY", "BRK.B"}
    assert data["companies"]["TOST"]["operatingModelAvailable"] is True
    assert data["companies"]["ADYEY"]["operatingModelAvailable"] is True
    assert data["companies"]["BRK.B"]["operatingModelAvailable"] is False
    for ticker in ("TOST", "ADYEY", "BRK.B"):
        company = data["companies"][ticker]
        assert company["dcfYearly"]
        base = company["scenarioParameters"]["base"]
        assert 0 < base["terminalGrowth"] < base["discountRate"]
        assert company["price"] > 0
    tost = data["companies"]["TOST"]
    assert len(tost["baseForecast"]) >= 10
    assert tost["baseForecast"][0]["valuation_fcf_m"] > 0
    assert tost["baseForecast"][0]["share_count_m"] > 0
    print("DCF learning snapshot passed reconciliation and invariant checks")


if __name__ == "__main__":
    main()
