import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / "src/data/dcf-learning.json").read_text())
TOST = SNAPSHOT["companies"]["TOST"]


def profit_path(starting_gross_profit, gross_profit_growth, starting_costs, cost_growth, years=5):
    rows = []
    for index in range(years):
        gross_profit = starting_gross_profit * ((1 + gross_profit_growth) ** index)
        costs = starting_costs * ((1 + cost_growth) ** index)
        rows.append(gross_profit - costs)
    return rows


def buyback_bridge(operating_value, owner_cash, starting_shares, sbc_dollars, sbc_price, buyback_cash, buyback_price):
    spend = min(owner_cash, buyback_cash)
    starting_equity = operating_value + owner_cash
    sbc_shares = sbc_dollars / sbc_price
    no_buyback_shares = starting_shares + sbc_shares
    no_buyback_value_per_share = starting_equity / no_buyback_shares
    repurchased = spend / buyback_price
    ending_shares = no_buyback_shares - repurchased
    ending_equity = starting_equity - spend
    return {
        "ending_cash": owner_cash - spend,
        "ending_shares": ending_shares,
        "no_buyback_value_per_share": no_buyback_value_per_share,
        "ending_value_per_share": ending_equity / ending_shares,
    }


class ToastSpineMathTests(unittest.TestCase):
    def test_historical_profit_inflection_matches_snapshot(self):
        history = {row["period"]: row["operating_income_m"] for row in TOST["historical"]}
        self.assertEqual(history["FY2022"], -384.0)
        self.assertEqual(history["FY2024"], 16.0)
        self.assertEqual(history["FY2025"], 292.0)

    def test_economic_gross_profit_approximately_reconciles_to_operating_income(self):
        first = TOST["baseForecast"][0]
        economic_gross_profit = (
            first["subscription_gross_profit_m"]
            + first["fintech_gross_profit_m"]
            + first["hardware_services_gross_profit_m"]
        )
        modeled_operating_costs = (
            first["sales_marketing_m"]
            + first["research_development_m"]
            + first["general_admin_m"]
        )
        teaching_operating_income = economic_gross_profit - modeled_operating_costs
        self.assertAlmostEqual(teaching_operating_income, first["operating_income_m"], delta=5.1)

    def test_gross_profit_outgrowing_costs_creates_operating_leverage(self):
        profits = profit_path(1_844, 0.20, 1_438, 0.09)
        self.assertGreater(profits[-1], profits[0])

    def test_revenue_or_gross_profit_growth_alone_does_not_guarantee_profit_growth(self):
        profits = profit_path(1_844, 0.10, 1_438, 0.20)
        self.assertLess(profits[-1], profits[0])

    def test_buyback_spends_cash_before_reducing_shares(self):
        result = buyback_bridge(19_000, 1_500, 602, 251, 25, 500, 25)
        self.assertEqual(result["ending_cash"], 1_000)
        self.assertLess(result["ending_shares"], 602)

    def test_below_value_buyback_improves_per_share_value_relative_to_no_buyback(self):
        result = buyback_bridge(19_000, 1_500, 602, 251, 25, 500, 20)
        self.assertGreater(result["ending_value_per_share"], result["no_buyback_value_per_share"])

    def test_above_value_buyback_destroys_per_share_value_relative_to_no_buyback(self):
        result = buyback_bridge(19_000, 1_500, 602, 251, 25, 500, 50)
        self.assertLess(result["ending_value_per_share"], result["no_buyback_value_per_share"])

    def test_sbc_can_outpace_buybacks(self):
        result = buyback_bridge(19_000, 1_500, 602, 500, 20, 100, 25)
        self.assertGreater(result["ending_shares"], 602)


if __name__ == "__main__":
    unittest.main()
