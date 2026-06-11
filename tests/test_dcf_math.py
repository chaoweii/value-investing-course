import unittest


def dcf_value(fcf, discount_rate, terminal_growth, net_cash=0):
    pv = sum(value / ((1 + discount_rate) ** (index + 1)) for index, value in enumerate(fcf))
    terminal = fcf[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    return pv + terminal / ((1 + discount_rate) ** len(fcf)) + net_cash


class DcfMathTests(unittest.TestCase):
    def test_higher_discount_rate_reduces_value(self):
        flows = [100, 110, 120, 130, 140]
        self.assertGreater(dcf_value(flows, 0.09, 0.03), dcf_value(flows, 0.11, 0.03))

    def test_higher_growth_increases_value(self):
        self.assertGreater(dcf_value([100, 120, 144], 0.10, 0.03), dcf_value([100, 105, 110], 0.10, 0.03))

    def test_owner_cash_added_once(self):
        flows = [100, 110, 120]
        self.assertAlmostEqual(dcf_value(flows, 0.10, 0.03, 50) - dcf_value(flows, 0.10, 0.03), 50)

    def test_terminal_growth_must_remain_below_discount_rate(self):
        with self.assertRaises(ZeroDivisionError):
            dcf_value([100, 110], 0.10, 0.10)


if __name__ == "__main__":
    unittest.main()
