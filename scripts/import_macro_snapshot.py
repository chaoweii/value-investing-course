#!/usr/bin/env python3
"""Import a dated macro snapshot from official/public institutional sources."""

from __future__ import annotations

import csv
import io
import json
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "src/data/macro-snapshot.json"
TREASURY_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    f"pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value={datetime.now().year}"
)
FRED_URL = (
    "https://fred.stlouisfed.org/graph/fredgraph.csv?"
    f"cosd={datetime.now().year - 1}-01-01&id="
)
FRED_LABELS = {
    "DFF": "Effective federal funds rate",
    "DFII10": "10-year real Treasury yield",
    "T10YIE": "10-year breakeven inflation",
    "MORTGAGE30US": "30-year fixed mortgage rate",
    "BAMLH0A0HYM2": "US high-yield option-adjusted spread",
}
CURVE_FIELDS = {
    "1M": "BC_1MONTH",
    "3M": "BC_3MONTH",
    "6M": "BC_6MONTH",
    "1Y": "BC_1YEAR",
    "2Y": "BC_2YEAR",
    "5Y": "BC_5YEAR",
    "10Y": "BC_10YEAR",
    "20Y": "BC_20YEAR",
    "30Y": "BC_30YEAR",
}


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "OwnerMindsetCourse/0.1"})
    certificate_bundle = Path("/opt/homebrew/etc/ca-certificates/cert.pem")
    if not certificate_bundle.exists():
        certificate_bundle = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(certificate_bundle))
    with urllib.request.urlopen(request, timeout=30, context=context) as response:
        return response.read().decode("utf-8")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_treasury_xml(text: str) -> dict:
    root = ET.fromstring(text)
    rows = []
    for properties in root.iter():
        if local_name(properties.tag) != "properties":
            continue
        record = {local_name(child.tag): (child.text or "").strip() for child in properties}
        if record.get("NEW_DATE"):
            rows.append(record)
    if not rows:
        raise ValueError("Treasury source did not contain yield-curve rows")
    latest = max(rows, key=lambda row: row["NEW_DATE"])
    curve = []
    for maturity, field in CURVE_FIELDS.items():
        value = latest.get(field, "")
        if value:
            curve.append({"maturity": maturity, "yield": float(value)})
    if not curve:
        raise ValueError("Treasury source did not contain curve values")
    return {"asOf": latest["NEW_DATE"][:10], "curve": curve}


def parse_fred_csv(text: str) -> dict:
    reader = csv.DictReader(io.StringIO(text))
    latest: dict[str, dict] = {}
    for row in reader:
        date = row.get("observation_date", "")
        for series, label in FRED_LABELS.items():
            value = row.get(series, "").strip()
            if value and value != ".":
                latest[series] = {"series": series, "label": label, "asOf": date, "value": float(value)}
    if not latest:
        raise ValueError("FRED source did not contain usable observations")
    return latest


def main() -> None:
    warnings = []
    existing = {}
    if OUTPUT.exists():
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))

    try:
        treasury = parse_treasury_xml(fetch(TREASURY_URL))
    except Exception as exc:  # network and source failures must not erase the last good snapshot
        treasury = existing.get("treasury", {"asOf": "", "curve": []})
        warnings.append(f"Treasury refresh failed; retained prior snapshot. {exc}")

    try:
        indicators = {}
        for series in FRED_LABELS:
            indicators.update(parse_fred_csv(fetch(f"{FRED_URL}{series}")))
    except Exception as exc:
        indicators = existing.get("indicators", {})
        warnings.append(f"FRED refresh failed; retained prior snapshot. {exc}")

    payload = {
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sources": {
            "treasury": TREASURY_URL,
            "fred": "https://fred.stlouisfed.org/",
        },
        "warnings": warnings,
        "treasury": treasury,
        "indicators": indicators,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    for warning in warnings:
        print(f"Warning: {warning}")


if __name__ == "__main__":
    main()
