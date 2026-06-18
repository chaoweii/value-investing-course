import math
import unittest


def max_drawdown(wealth_series):
    peak = wealth_series[0]
    worst = 0
    for wealth in wealth_series:
        peak = max(peak, wealth)
        worst = min(worst, wealth / peak - 1)
    return worst


def worst_rolling_cagr(wealth_series, period):
    values = []
    for index in range(period, len(wealth_series)):
        values.append((wealth_series[index] / wealth_series[index - period]) ** (1 / period) - 1)
    return min(values)


def valuation_weight(previous_cape, low=15, high=25, minimum=0.3, normal=0.6, maximum=0.9):
    if previous_cape <= low:
        return maximum
    if previous_cape >= high:
        return minimum
    return normal


def spread_weight(previous_pe, previous_tbill_yield, hurdle=0.02, minimum=0.3, normal=0.6, maximum=0.9):
    earnings_yield = 1 / previous_pe
    spread = earnings_yield - previous_tbill_yield
    if spread >= hurdle:
        return maximum
    if spread <= 0:
        return minimum
    return normal


def simulate_two_years(records):
    wealth = 100
    weights = []
    for index in range(1, len(records)):
        previous = records[index - 1]
        current = records[index]
        weight = valuation_weight(previous["cape"])
        weights.append(weight)
        blended_return = weight * current["sp_return"] + (1 - weight) * current["tbill_return"]
        wealth *= 1 + blended_return
    return wealth, weights


class CycleSimulatorMathTests(unittest.TestCase):
    def test_reinvested_returns_compound_geometrically(self):
        wealth = 10000 * (1 + 0.10) * (1 - 0.20) * (1 + 0.25)
        self.assertAlmostEqual(wealth, 11000)

    def test_max_drawdown_uses_prior_peak(self):
        self.assertAlmostEqual(max_drawdown([100, 120, 90, 150]), -0.25)

    def test_worst_rolling_return_is_geometric(self):
        wealth = [100, 110, 121, 100]
        self.assertAlmostEqual(worst_rolling_cagr(wealth, 2), (100 / 110) ** 0.5 - 1)

    def test_valuation_thresholds_change_equity_weight(self):
        self.assertEqual(valuation_weight(12), 0.9)
        self.assertEqual(valuation_weight(20), 0.6)
        self.assertEqual(valuation_weight(30), 0.3)

    def test_earnings_yield_spread_compares_to_tbill_opportunity_cost(self):
        self.assertEqual(spread_weight(previous_pe=10, previous_tbill_yield=0.03), 0.9)
        self.assertEqual(spread_weight(previous_pe=40, previous_tbill_yield=0.04), 0.3)

    def test_allocation_uses_prior_year_valuation_not_future_data(self):
        base_records = [
            {"cape": 10, "sp_return": 0.0, "tbill_return": 0.0},
            {"cape": 50, "sp_return": 0.2, "tbill_return": 0.04},
        ]
        changed_current_valuation = [
            {"cape": 10, "sp_return": 0.0, "tbill_return": 0.0},
            {"cape": 5, "sp_return": 0.2, "tbill_return": 0.04},
        ]
        base_wealth, base_weights = simulate_two_years(base_records)
        changed_wealth, changed_weights = simulate_two_years(changed_current_valuation)
        self.assertEqual(base_weights, changed_weights)
        self.assertAlmostEqual(base_wealth, changed_wealth)


if __name__ == "__main__":
    unittest.main()
