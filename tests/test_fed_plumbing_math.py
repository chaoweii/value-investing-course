import unittest


def reserve_change(securities_change, on_rrp_change=0, tga_change=0, currency_change=0):
    """Simplified teaching identity in billions of dollars.

    Positive means bank reserves rise. Negative means bank reserves fall.
    """
    return securities_change - tga_change - currency_change - on_rrp_change


def interbank_payment(bank_a_reserves, bank_b_reserves, payment_amount):
    return bank_a_reserves - payment_amount, bank_b_reserves + payment_amount


def private_repo(cash_holder_cash, dealer_cash, collateral_amount, cash_amount):
    """Private repo reallocates cash and collateral; it does not create Fed reserves."""
    return {
        "cash_holder_cash": cash_holder_cash - cash_amount,
        "dealer_cash": dealer_cash + cash_amount,
        "cash_holder_collateral": collateral_amount,
        "new_fed_reserves": 0,
    }


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

    def test_customer_payment_moves_reserves_between_banks(self):
        bank_a, bank_b = interbank_payment(500, 300, 100)
        self.assertEqual(bank_a, 400)
        self.assertEqual(bank_b, 400)

    def test_normal_payment_does_not_change_total_system_reserves(self):
        before = 500 + 300
        bank_a, bank_b = interbank_payment(500, 300, 100)
        after = bank_a + bank_b
        self.assertEqual(before, after)

    def test_fed_repo_increases_reserves_temporarily(self):
        self.assertEqual(reserve_change(securities_change=25), 25)

    def test_private_repo_does_not_create_fed_reserves(self):
        result = private_repo(
            cash_holder_cash=100,
            dealer_cash=10,
            collateral_amount=100,
            cash_amount=95,
        )
        self.assertEqual(result["cash_holder_cash"], 5)
        self.assertEqual(result["dealer_cash"], 105)
        self.assertEqual(result["cash_holder_collateral"], 100)
        self.assertEqual(result["new_fed_reserves"], 0)


if __name__ == "__main__":
    unittest.main()
