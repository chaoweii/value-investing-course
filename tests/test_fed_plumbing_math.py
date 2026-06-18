import unittest


def reserve_change(securities_change, on_rrp_change=0, tga_change=0, currency_change=0):
    """Simplified teaching identity in billions of dollars.

    Positive means bank reserves rise. Negative means bank reserves fall.
    """
    return securities_change - tga_change - currency_change - on_rrp_change


class FedPlumbingMathTests(unittest.TestCase):
    def test_qe_purchase_usually_creates_reserves(self):
        self.assertEqual(reserve_change(securities_change=100), 100)

    def test_qt_runoff_usually_drains_reserves(self):
        self.assertEqual(reserve_change(securities_change=-60), -60)

    def test_on_rrp_decline_offsets_reserve_drain(self):
        self.assertEqual(reserve_change(securities_change=-60, on_rrp_change=-40), -20)

    def test_tga_increase_drains_reserves(self):
        self.assertEqual(reserve_change(securities_change=0, tga_change=30), -30)

    def test_currency_demand_drains_reserves(self):
        self.assertEqual(reserve_change(securities_change=0, currency_change=10), -10)

    def test_combined_example_matches_lesson(self):
        self.assertEqual(
            reserve_change(
                securities_change=-60,
                on_rrp_change=-40,
                tga_change=30,
                currency_change=10,
            ),
            -60,
        )


if __name__ == "__main__":
    unittest.main()
