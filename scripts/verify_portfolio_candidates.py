#!/usr/bin/env python3
"""Sanity-check the stored portfolio-candidate snapshot."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "src/data/portfolio-candidates.json"


def main():
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    candidates = {row["ticker"]: row for row in payload["candidates"]}
    assert set(payload["curatedTickers"]).issubset(candidates)
    assert len(candidates) >= 30
    for row in candidates.values():
        assert abs(row["bearProbability"] + row["baseProbability"] + row["bullProbability"] - 1) < 1e-6
        assert row["themes"]
    assert candidates["CASH"]["bearFiveYearReturn"] == candidates["CASH"]["bullFiveYearReturn"]
    print("Portfolio candidate snapshot passed structural and probability checks")


if __name__ == "__main__":
    main()
