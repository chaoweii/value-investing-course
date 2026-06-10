import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/import_portfolio_candidates.py"
SPEC = importlib.util.spec_from_file_location("portfolio_import", SCRIPT)
portfolio_import = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(portfolio_import)


class PortfolioMathTests(unittest.TestCase):
    def test_recovery_required_is_nonlinear(self):
        self.assertAlmostEqual(portfolio_import.recovery_required(0.2), 0.25)
        self.assertAlmostEqual(portfolio_import.recovery_required(0.5), 1.0)
        self.assertAlmostEqual(portfolio_import.recovery_required(0.75), 3.0)

    def test_risk_themes_reveal_hidden_concentration(self):
        self.assertIn("Payments / fintech", portfolio_import.risk_themes("TOST"))
        self.assertIn("Long-duration growth", portfolio_import.risk_themes("ADYEY"))
        self.assertIn("China / VIE", portfolio_import.risk_themes("PDD"))

    def test_weighted_outcome_and_correlated_stress(self):
        weights = {"A": 50, "B": 50}
        independent = portfolio_import.weighted_outcome(weights, {"A": -0.4, "B": 0.5})
        correlated = portfolio_import.weighted_outcome(weights, {"A": -0.4, "B": -0.4})
        self.assertAlmostEqual(independent, 0.05)
        self.assertLess(correlated, independent)

    def test_teaching_position_cap_uses_most_conservative_tier(self):
        policy = {
            "monitorMaximum": 2, "watchMaximum": 5, "staged": 5, "core": 10,
        }
        watch_core = {
            "ticker": "EXAMPLE", "asymmetryVerdict": "Core candidate",
            "committeeVerdict": "Watch with proof",
        }
        cash = {
            "ticker": "CASH", "asymmetryVerdict": "Dry powder",
            "committeeVerdict": "Capital preservation",
        }
        self.assertEqual(portfolio_import.teaching_position_cap(watch_core, policy), 5)
        self.assertEqual(portfolio_import.teaching_position_cap(cash, policy), 100)


if __name__ == "__main__":
    unittest.main()
