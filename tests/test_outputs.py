import unittest
import os
import pandas as pd
from pathlib import Path
from src import config

class TestPipelineOutputs(unittest.TestCase):
    
    def setUp(self):
        self.results_dir = config.RESULTS_DIR
        self.csv_path = self.results_dir / "ndvi_data.csv"
        self.plot_path = self.results_dir / "ndvi_plot.png"

    def test_results_exist(self):
        """Test that output files exist."""
        self.assertTrue(self.csv_path.exists(), f"CSV file not found at {self.csv_path}")
        self.assertTrue(self.plot_path.exists(), f"Plot file not found at {self.plot_path}")

    def test_csv_validity(self):
        """Test that the CSV contains valid data."""
        if not self.csv_path.exists():
            self.skipTest("CSV file does not exist")

        df = pd.read_csv(self.csv_path)
        
        # Check columns
        expected_cols = ["date", "mean_ndvi", "ndvi_smoothed"]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Column {col} missing from CSV")

        # Check NDVI range
        # NDVI must be between -1 and 1
        invalid_ndvi = df[(df["mean_ndvi"] < -1) | (df["mean_ndvi"] > 1)]
        self.assertTrue(invalid_ndvi.empty, f"Found invalid NDVI values:\n{invalid_ndvi}")

        # Check date format
        try:
            pd.to_datetime(df["date"])
        except Exception as e:
            self.fail(f"Date column contains invalid dates: {e}")

if __name__ == "__main__":
    unittest.main()
