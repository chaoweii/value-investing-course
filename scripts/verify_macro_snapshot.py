#!/usr/bin/env python3
"""Validate the stored macro companion without contacting external sources."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "src/data/macro-snapshot.json"
REQUIRED_SERIES = {"DFF", "DFII10", "T10YIE", "MORTGAGE30US", "BAMLH0A0HYM2"}


def main() -> None:
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    curve = {point["maturity"]: point["yield"] for point in payload["treasury"]["curve"]}
    indicators = payload["indicators"]

    assert {"1M", "2Y", "10Y", "30Y"}.issubset(curve), "Stored curve is incomplete"
    assert REQUIRED_SERIES.issubset(indicators), "Stored macro indicators are incomplete"
    assert all(0 < value < 25 for value in curve.values()), "Curve contains an implausible yield"
    assert all(0 <= item["value"] < 30 for item in indicators.values()), "Indicator value is implausible"
    assert date.fromisoformat(payload["treasury"]["asOf"]) <= date.today(), "Curve date is in the future"

    decomposition_gap = abs(
        curve["10Y"] - indicators["DFII10"]["value"] - indicators["T10YIE"]["value"]
    )
    assert decomposition_gap < 1.5, "Nominal-real-breakeven relationship needs review"
    print("Stored macro snapshot passed structural and sanity checks")


if __name__ == "__main__":
    main()
