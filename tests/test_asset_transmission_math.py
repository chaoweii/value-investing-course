import unittest


def bond_duration_price_change(duration, yield_change_bps):
    return -duration * (yield_change_bps / 10000)


def mortgage_payment(principal, annual_rate, years=30):
    months = years * 12
    monthly_rate = annual_rate / 100 / 12
    if monthly_rate == 0:
        return principal / months
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)


def reserve_change(asset_change, currency_change=0, tga_change=0, on_rrp_change=0, other_liability_change=0):
    return asset_change - currency_change - tga_change - on_rrp_change - other_liability_change


class AssetTransmissionMathTests(unittest.TestCase):
    def test_duration_rule_of_thumb(self):
        self.assertAlmostEqual(bond_duration_price_change(8, 100), -0.08)
        self.assertAlmostEqual(bond_duration_price_change(8, -100), 0.08)

    def test_mortgage_rate_increase_raises_payment(self):
        principal = 600000 * 0.8
        low_rate = mortgage_payment(principal, 5.5)
        high_rate = mortgage_payment(principal, 6.5)
        self.assertGreater(high_rate, low_rate)
        self.assertGreater(high_rate - low_rate, 250)

    def test_qt_reserve_change_depends_on_other_liabilities(self):
        base = reserve_change(asset_change=-60, on_rrp_change=-40, tga_change=30, currency_change=10)
        more_rrp_absorption = reserve_change(asset_change=-60, on_rrp_change=-80, tga_change=30, currency_change=10)
        self.assertEqual(base, -60)
        self.assertEqual(more_rrp_absorption, -20)

    def test_tga_rebuild_drains_reserves(self):
        self.assertEqual(reserve_change(asset_change=0, tga_change=50), -50)


if __name__ == "__main__":
    unittest.main()
