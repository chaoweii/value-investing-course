#!/usr/bin/env python3
"""Build a read-only DCF teaching snapshot from valuation-workbench outputs."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = Path("/Users/chao86/Documents/Investment 2/tost_googl_sotp_dcf")
OUTPUTS = WORKBENCH / "outputs"
MASTER = OUTPUTS / "data/master_portfolio_valuation.csv"
OUTPUT = ROOT / "src/data/dcf-learning.json"
TICKERS = ("TOST", "ADYEY", "BRK.B")


def number(value: str | None) -> float | None:
    return float(value) if value not in (None, "") else None


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def select_fields(row: dict[str, str], fields: tuple[str, ...]) -> dict:
    return {field: number(row.get(field)) if field not in {"period", "row_type", "scenario", "year"} else row.get(field, "")
            for field in fields}


def parse_scenario_parameters(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    result = {}
    for scenario in ("Bear", "Base", "Bull"):
        match = re.search(rf"### {scenario}\n(.*?)(?=\n### |\n## )", text, re.S)
        if not match:
            continue
        block = match.group(1)
        parameters = {}
        for label, key in (
            ("Discount rate", "discountRate"),
            ("Terminal growth", "terminalGrowth"),
            ("Net cash / investments included", "netCashM"),
            ("2026 valuation FCF from driver table", "anchorFcfM"),
        ):
            value = re.search(rf"- {re.escape(label)}: \$?([\d.]+)([BM]?)%?", block)
            if value:
                amount = float(value.group(1))
                if value.group(2) == "B":
                    amount *= 1000
                if key in {"discountRate", "terminalGrowth"}:
                    amount /= 100
                parameters[key] = amount
        result[scenario.lower()] = parameters
    return result


def company_snapshot(ticker: str, master: dict[str, str]) -> dict:
    operating_path = OUTPUTS / f"operating_models/{ticker}_operating_model.csv"
    dcf_path = OUTPUTS / f"dcf/{ticker}_dcf_yearly.csv"
    target_path = OUTPUTS / f"dcf/{ticker}_target_prices.csv"
    report_path = OUTPUTS / f"dcf/{ticker}_dcf_valuation.md"
    operating = read_csv(operating_path)
    dcf = read_csv(dcf_path)
    targets = read_csv(target_path)
    historical_fields = (
        "period", "year", "row_type", "revenue_m", "operating_income_m",
        "operating_cash_flow_m", "capex_m", "free_cash_flow_m", "operating_margin",
    )
    forecast_fields = (
        "period", "year", "scenario", "revenue_m", "cost_of_revenue_m",
        "sales_marketing_m", "research_development_m", "general_admin_m",
        "operating_income_m", "operating_margin", "tax_cash_m", "capex_m",
        "working_capital_m", "leases_m", "owner_fcf_m",
        "required_sbc_offset_buyback_m", "valuation_fcf_m", "net_cash_m",
        "share_count_m", "owner_fcf_per_share", "ending_locations_k",
        "net_added_locations_k", "gpv_bn", "gpv_per_location_m",
        "subscription_gross_profit_m", "fintech_gross_profit_m",
        "hardware_services_gross_profit_m",
    )
    historical = [select_fields(row, historical_fields) for row in operating if row.get("row_type") == "historical_reported"]
    base_forecast = [select_fields(row, forecast_fields) for row in operating if row.get("scenario") == "base"]
    yearly = [{
        "scenario": row["scenario"], "year": int(row["year"]), "fcfM": number(row["fcf_m"]),
        "growth": number(row["growth"]), "discountFactor": number(row["discount_factor"]),
        "pvFcfM": number(row["pv_fcf_m"]),
    } for row in dcf]
    target_prices = [{
        "scenario": row["scenario"], "method": row["valuation_method"],
        "horizonYears": number(row["horizon_years"]), "targetPrice": number(row["target_price"]),
        "cagr": number(row["cagr"]), "sharesM": number(row["shares_m"]),
    } for row in targets]
    return {
        "ticker": ticker,
        "company": master["company"],
        "currency": master["currency"],
        "sourceDate": master["last_updated"],
        "price": number(master["price"]),
        "bearValue": number(master["current_dcf_bear"]),
        "baseValue": number(master["current_dcf_base"]),
        "bullValue": number(master["current_dcf_bull"]),
        "baseSotp": number(master["current_sotp_base"]),
        "baseFiveYearCagr": number(master["base_5y_cagr"]),
        "benchmarkGate": master["benchmark_gate"],
        "operatingModelAvailable": operating_path.exists(),
        "historical": historical,
        "baseForecast": base_forecast,
        "dcfYearly": yearly,
        "targetPrices": target_prices,
        "scenarioParameters": parse_scenario_parameters(report_path),
        "sources": {
            "operatingModel": str(operating_path),
            "dcfYearly": str(dcf_path),
            "targetPrices": str(target_path),
            "dcfReport": str(report_path),
        },
    }


def main() -> None:
    master_rows = read_csv(MASTER)
    master = {row["ticker"]: row for row in master_rows}
    missing = [ticker for ticker in TICKERS if ticker not in master]
    if missing:
        raise ValueError(f"Missing master valuation rows: {', '.join(missing)}")
    companies = {ticker: company_snapshot(ticker, master[ticker]) for ticker in TICKERS}
    payload = {
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sourceWorkspace": str(WORKBENCH),
        "readOnly": True,
        "companies": companies,
        "teachingDefaults": {
            "ticker": "TOST",
            "discountRate": companies["TOST"]["scenarioParameters"].get("base", {}).get("discountRate", 0.102),
            "terminalGrowth": companies["TOST"]["scenarioParameters"].get("base", {}).get("terminalGrowth", 0.032),
            "forecastYears": 10,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} from read-only workbench outputs")


if __name__ == "__main__":
    main()
