import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/import_macro_snapshot.py"
SPEC = importlib.util.spec_from_file_location("macro_import", SCRIPT)
macro_import = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(macro_import)


class MacroImportTests(unittest.TestCase):
    def fixture(self, name):
        return (Path(__file__).parent / "fixtures" / name).read_text(encoding="utf-8")

    def test_treasury_parser_uses_latest_curve(self):
        parsed = macro_import.parse_treasury_xml(self.fixture("treasury.xml"))
        self.assertEqual(parsed["asOf"], "2026-06-09")
        values = {point["maturity"]: point["yield"] for point in parsed["curve"]}
        self.assertEqual(values["10Y"], 4.31)
        self.assertEqual(values["30Y"], 4.81)

    def test_fred_parser_keeps_latest_valid_value_per_series(self):
        parsed = macro_import.parse_fred_csv(self.fixture("fred.csv"))
        self.assertEqual(parsed["DFF"]["asOf"], "2026-06-07")
        self.assertEqual(parsed["DFII10"]["asOf"], "2026-06-06")
        self.assertEqual(parsed["MORTGAGE30US"]["asOf"], "2026-06-05")
        self.assertEqual(parsed["BAMLH0A0HYM2"]["value"], 3.12)

    def test_empty_sources_fail_closed(self):
        with self.assertRaises(ValueError):
            macro_import.parse_treasury_xml("<feed />")
        with self.assertRaises(ValueError):
            macro_import.parse_fred_csv("observation_date,DFF\n")


if __name__ == "__main__":
    unittest.main()
