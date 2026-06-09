#!/usr/bin/env python3
"""Read-only importer for dated valuation companion snapshots."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = Path("/Users/chao86/Documents/Investment 2/tost_googl_sotp_dcf")
MASTER = WORKBENCH / "outputs/data/master_portfolio_valuation.csv"
OUTPUT = ROOT / "src/data/live-companions.json"
TICKERS = ("TOST", "ADYEY", "BRK.B")


def number(row: dict[str, str], key: str) -> float | None:
    value = row.get(key, "").strip()
    return float(value) if value else None


def report_link(path: str) -> dict[str, str | bool]:
    if not path:
        return {"path": "", "uri": "", "exists": False}
    candidate = Path(path)
    try:
        relative = str(candidate.relative_to(WORKBENCH))
    except ValueError:
        relative = str(candidate)
    return {"path": relative, "uri": candidate.as_uri(), "exists": candidate.exists()}


def empty_snapshot(ticker: str) -> dict:
    unavailable = {"path": "", "uri": "", "exists": False}
    return {
        "ticker": ticker,
        "company": ticker,
        "currency": "USD",
        "sourceRefreshDate": "",
        "researchVersion": "",
        "price": None,
        "bearValue": None,
        "baseValue": None,
        "bullValue": None,
        "marginOfSafety": None,
        "baseFiveYearCagr": None,
        "baseTenYearCagr": None,
        "benchmarkGate": "Live valuation unavailable",
        "verdict": "No current snapshot",
        "currentRead": "The durable lesson remains available without live valuation data.",
        "reports": {
            "buySide": unavailable,
            "dcf": unavailable,
            "sotp": unavailable,
            "auditor": unavailable,
        },
    }


def main() -> None:
    import_warning = ""
    rows = {}
    if MASTER.exists():
        with MASTER.open(newline="", encoding="utf-8") as handle:
            rows = {row["ticker"]: row for row in csv.DictReader(handle) if row["ticker"] in TICKERS}
        missing = sorted(set(TICKERS) - set(rows))
        if missing:
            import_warning = f"Missing live valuation rows: {', '.join(missing)}"
    else:
        import_warning = f"Live valuation source is unavailable: {MASTER}"

    snapshots = {}
    for ticker in TICKERS:
        if ticker not in rows:
            snapshots[ticker] = empty_snapshot(ticker)
            continue
        row = rows[ticker]
        snapshots[ticker] = {
            "ticker": ticker,
            "company": row["company"],
            "currency": row["currency"],
            "sourceRefreshDate": row["last_updated"],
            "researchVersion": row["research_approach_version"],
            "price": number(row, "price"),
            "bearValue": number(row, "blended_bear_fv"),
            "baseValue": number(row, "blended_base_fv"),
            "bullValue": number(row, "blended_bull_fv"),
            "marginOfSafety": number(row, "mos_to_blended_base"),
            "baseFiveYearCagr": number(row, "base_5y_cagr"),
            "baseTenYearCagr": number(row, "base_10y_cagr"),
            "benchmarkGate": row["benchmark_gate"],
            "verdict": row["asymmetry_verdict"],
            "currentRead": row["current_read"],
            "reports": {
                "buySide": report_link(row["company_report_path"]),
                "dcf": report_link(row["dcf_report_path"]),
                "sotp": report_link(row["sotp_report_path"]),
                "auditor": report_link(
                    str(WORKBENCH / f"outputs/audits/{ticker}_conservative_auditor_report.md")
                ),
            },
        }

    payload = {
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": str(MASTER),
        "importWarning": import_warning,
        "snapshots": snapshots,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} from read-only source {MASTER}")
    if import_warning:
        print(f"Warning: {import_warning}")


if __name__ == "__main__":
    main()
