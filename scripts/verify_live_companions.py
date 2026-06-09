#!/usr/bin/env python3
"""Verify generated live snapshots reconcile to the read-only master CSV."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from import_live_companions import MASTER, OUTPUT, TICKERS


FIELDS = {
    "price": "price",
    "blended_bear_fv": "bearValue",
    "blended_base_fv": "baseValue",
    "blended_bull_fv": "bullValue",
    "mos_to_blended_base": "marginOfSafety",
    "base_5y_cagr": "baseFiveYearCagr",
    "base_10y_cagr": "baseTenYearCagr",
}


def main() -> None:
    with MASTER.open(newline="", encoding="utf-8") as handle:
        rows = {row["ticker"]: row for row in csv.DictReader(handle) if row["ticker"] in TICKERS}
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    for ticker in TICKERS:
        source = rows[ticker]
        snapshot = payload["snapshots"][ticker]
        for source_key, snapshot_key in FIELDS.items():
            expected = float(source[source_key])
            actual = snapshot[snapshot_key]
            if actual != expected:
                raise SystemExit(f"{ticker} {snapshot_key}: expected {expected}, found {actual}")
    print("Live companion snapshots reconcile to master_portfolio_valuation.csv")


if __name__ == "__main__":
    main()
