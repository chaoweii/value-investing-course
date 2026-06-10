#!/usr/bin/env python3
"""Build a read-only portfolio-candidate snapshot from valuation-workbench outputs."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = Path("/Users/chao86/Documents/Investment 2/tost_googl_sotp_dcf")
MASTER = WORKBENCH / "outputs/data/master_portfolio_valuation.csv"
PROBABILITY = WORKBENCH / "outputs/data/probability_weighted_returns.csv"
MACRO = ROOT / "src/data/macro-snapshot.json"
OUTPUT = ROOT / "src/data/portfolio-candidates.json"
CURATED = ("TOST", "ADYEY", "PDD", "TTD", "LEN", "FOUR", "BRK.B", "CASH")

THEMES = {
    "China / VIE": {"PDD", "FUTU", "JD", "BABA", "TCEHY", "0700.HK", "TCOM", "2388.HK", "1816.HK"},
    "Payments / fintech": {"TOST", "ADYEY", "FOUR", "FUTU", "PYPL", "FISV", "XYZ", "COIN", "CRCL", "MA", "V"},
    "Long-duration growth": {"TOST", "ADYEY", "TTD", "PLTR", "SHOP", "DASH", "ABNB", "CPNG", "NVDA", "TSLA", "ARM"},
    "Consumer cycle": {"TOST", "LULU", "PDD", "LEN", "BKNG", "ABNB", "TCOM", "NTDOY", "SONY", "COST"},
    "AI / capex": {"META", "GOOGL", "AMZN", "NVDA", "TSM", "MU", "PLTR", "ARM"},
    "Housing / rates": {"LEN", "BRK.B"},
}


def number(row: dict[str, str], key: str, default: float = 0.0) -> float:
    value = row.get(key, "").strip()
    return float(value) if value else default


def risk_themes(ticker: str) -> list[str]:
    matches = [theme for theme, tickers in THEMES.items() if ticker in tickers]
    return matches or ["Idiosyncratic / other"]


def recovery_required(loss: float) -> float:
    if loss >= 1:
        return float("inf")
    return loss / (1 - loss)


def weighted_outcome(weights: dict[str, float], outcomes: dict[str, float]) -> float:
    total = sum(weight for ticker, weight in weights.items() if ticker in outcomes)
    if not total:
        return 0.0
    return sum(weight / total * outcomes[ticker] for ticker, weight in weights.items() if ticker in outcomes)


def teaching_position_cap(candidate: dict, policy: dict[str, float]) -> float:
    if candidate["ticker"] == "CASH":
        return 100.0
    if candidate["asymmetryVerdict"] == "Monitor":
        return policy["monitorMaximum"]
    if candidate["committeeVerdict"] == "Watch with proof":
        return policy["watchMaximum"]
    if candidate["asymmetryVerdict"] == "Stage candidate":
        return policy["staged"]
    return policy["core"]


def main() -> None:
    with MASTER.open(newline="", encoding="utf-8") as handle:
        master = {row["ticker"]: row for row in csv.DictReader(handle)}
    with PROBABILITY.open(newline="", encoding="utf-8") as handle:
        probability = {row["ticker"]: row for row in csv.DictReader(handle)}
    macro = json.loads(MACRO.read_text(encoding="utf-8"))
    cash_yield = next(
        (point["yield"] / 100 for point in macro["treasury"]["curve"] if point["maturity"] == "3M"),
        0.03,
    )

    candidates = []
    for ticker, row in master.items():
        if row["asymmetry_verdict"] == "Pass" and ticker != "BRK.B":
            continue
        dynamic = probability.get(ticker, {})
        candidate = {
            "ticker": ticker,
            "company": row["company"],
            "asymmetryVerdict": row["asymmetry_verdict"],
            "committeeVerdict": row["committee_audit_verdict"],
            "dataQuality": row["data_quality_tier"],
            "isChina": row["is_china_company"] == "True",
            "themes": risk_themes(ticker),
            "price": number(row, "price"),
            "bearValue": number(row, "blended_bear_fv"),
            "baseValue": number(row, "blended_base_fv"),
            "bullValue": number(row, "blended_bull_fv"),
            "bearProbability": number(row, "bear_probability", 0.25),
            "baseProbability": number(row, "base_probability", 0.5),
            "bullProbability": number(row, "bull_probability", 0.25),
            "bearFiveYearReturn": number(row, "return_5y_bear"),
            "baseFiveYearReturn": number(row, "return_5y_base"),
            "bullFiveYearReturn": number(row, "return_5y_bull"),
            "expectedFiveYearReturn": number(row, "expected_5y_return"),
            "expectedFiveYearCagr": number(dynamic, "expected_5y_cagr", number(row, "expected_5y_cagr")),
            "sourceDate": row["last_updated"],
        }
        candidates.append(candidate)

    candidates.append({
        "ticker": "CASH",
        "company": "Cash / 3-month Treasury",
        "asymmetryVerdict": "Dry powder",
        "committeeVerdict": "Capital preservation",
        "dataQuality": "official_full",
        "isChina": False,
        "themes": ["Liquidity / opportunity cost"],
        "price": 1.0,
        "bearValue": (1 + cash_yield) ** 5,
        "baseValue": (1 + cash_yield) ** 5,
        "bullValue": (1 + cash_yield) ** 5,
        "bearProbability": 0.0,
        "baseProbability": 1.0,
        "bullProbability": 0.0,
        "bearFiveYearReturn": (1 + cash_yield) ** 5 - 1,
        "baseFiveYearReturn": (1 + cash_yield) ** 5 - 1,
        "bullFiveYearReturn": (1 + cash_yield) ** 5 - 1,
        "expectedFiveYearReturn": (1 + cash_yield) ** 5 - 1,
        "expectedFiveYearCagr": cash_yield,
        "sourceDate": macro["treasury"]["asOf"],
    })

    payload = {
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sources": [str(MASTER), str(PROBABILITY), str(MACRO)],
        "curatedTickers": CURATED,
        "policyDefaults": {
            "starter": 2, "staged": 5, "core": 10, "exceptional": 15,
            "themeMaximum": 25, "chinaMaximum": 10, "watchMaximum": 5,
            "monitorMaximum": 2, "bearLossBudget": 20,
        },
        "recoveryExamples": [
            {"loss": loss, "recoveryRequired": recovery_required(loss)}
            for loss in (0.1, 0.2, 0.3, 0.5, 0.75)
        ],
        "candidates": sorted(candidates, key=lambda item: item["ticker"]),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} from read-only workbench sources")


if __name__ == "__main__":
    main()
