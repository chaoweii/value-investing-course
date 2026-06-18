import unittest


def execute_order(demand, max_bid, supply_levels):
    remaining = demand
    executed = 0
    for price, supply in sorted(supply_levels):
        if price > max_bid:
            continue
        fill = min(supply, remaining)
        executed += fill
        remaining -= fill
    return executed, remaining


def etf_underlying_flow(mode, shares, nav):
    if mode == "secondary":
        return 0
    return shares * nav * (1 if mode == "creation" else -1)


def index_need(aum_m, target_weight, price, existing_m, derivative_m):
    target_m = aum_m * target_weight / price
    return max(0, target_m - existing_m - derivative_m)


class MarketMathTests(unittest.TestCase):
    def test_zero_willing_sellers_means_zero_trades(self):
        self.assertEqual(execute_order(1000, 105, [(110, 1000)]), (0, 1000))

    def test_higher_bid_reaches_more_supply(self):
        low = execute_order(1000, 100, [(100, 200), (105, 1000)])
        high = execute_order(1000, 105, [(100, 200), (105, 1000)])
        self.assertLess(low[0], high[0])
        self.assertEqual(high[1], 0)

    def test_secondary_etf_trade_does_not_force_basket_flow(self):
        self.assertEqual(etf_underlying_flow("secondary", 100000, 100), 0)
        self.assertGreater(etf_underlying_flow("creation", 100000, 100), 0)
        self.assertLess(etf_underlying_flow("redemption", 100000, 100), 0)

    def test_existing_and_derivative_exposure_reduce_physical_need(self):
        self.assertEqual(index_need(500000, 0.02, 100, 10, 15), 75)


if __name__ == "__main__":
    unittest.main()
