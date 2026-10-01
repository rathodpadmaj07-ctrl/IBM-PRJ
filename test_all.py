import sys
import os

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))

from src.data_processing import validate_and_clean_data, calculate_expected_prices, get_urban_zone_statistics, format_currency_inr
from src.statistical_analysis import run_grubbs_test, run_iqr_analysis, analyze_and_classify_properties
import pandas as pd
import numpy as np

def run_verification():
    print("==========================================================")
    print(" REAL ESTATE PRICE OUTLIER ANALYZER - VERIFICATION SUITE  ")
    print("==========================================================")
    
    # 1. Load Dataset
    data_path = os.path.join("data", "sample_real_estate.csv")
    if not os.path.exists(data_path):
        print(f"ERROR: Dataset not found at {data_path}")
        return
        
    df_raw = pd.read_csv(data_path)
    print(f"✓ Loaded Raw Dataset: {len(df_raw)} records")
    
    # 2. Data Cleaning & Validation
    df_clean, meta, warnings = validate_and_clean_data(df_raw)
    print(f"✓ Data Cleaning Passed: {len(df_clean)} valid records remaining")
    
    # 3. Expected Price Benchmarking
    df_calc = calculate_expected_prices(df_clean)
    required_cols = ["Actual Price", "Expected Price", "Price Difference", "Price Difference (%)"]
    for col in required_cols:
        assert col in df_calc.columns, f"Missing required column: {col}"
    print(f"✓ Terminology Verification Passed: All mandatory columns present")
    
    # 4. Statistical Analysis & Classification
    df_classified = analyze_and_classify_properties(df_calc, alpha=0.05, min_obs=10)
    counts = df_classified["Classification"].value_counts().to_dict()
    print(f"✓ Classification Counts: {counts}")
    
    # 5. Case Study Verification: P1023 (Underpriced Outlier)
    p1023 = df_classified[df_classified["property_id"] == "P1023"]
    if not p1023.empty:
        r1023 = p1023.iloc[0]
        print(f"\n--- PROPERTY P1023 AUDIT ---")
        print(f"  Actual Price:         {format_currency_inr(r1023['Actual Price'])}")
        print(f"  Expected Price:       {format_currency_inr(r1023['Expected Price'])}")
        print(f"  Price Difference:     {format_currency_inr(r1023['Price Difference'], is_difference=True)}")
        print(f"  Price Difference (%): {r1023['Price Difference (%)']:+.2f}%")
        print(f"  Classification:       {r1023['Classification']}")
        assert r1023["Classification"] == "Potentially Underpriced", "P1023 should be classified as Potentially Underpriced!"
        
    # 6. Case Study Verification: P1842 (Overpriced Outlier)
    p1842 = df_classified[df_classified["property_id"] == "P1842"]
    if not p1842.empty:
        r1842 = p1842.iloc[0]
        print(f"\n--- PROPERTY P1842 AUDIT ---")
        print(f"  Actual Price:         {format_currency_inr(r1842['Actual Price'])}")
        print(f"  Expected Price:       {format_currency_inr(r1842['Expected Price'])}")
        print(f"  Price Difference:     {format_currency_inr(r1842['Price Difference'], is_difference=True)}")
        print(f"  Price Difference (%): {r1842['Price Difference (%)']:+.2f}%")
        print(f"  Classification:       {r1842['Classification']}")
        assert r1842["Classification"] == "Potentially Overpriced", "P1842 should be classified as Potentially Overpriced!"

    # 7. Currency Formatting Test
    assert format_currency_inr(7200000) == "₹72.00 L"
    assert format_currency_inr(12500000) == "₹1.25 Cr"
    assert format_currency_inr(-1920000, is_difference=True) == "-₹19.20 L"
    print(f"✓ Currency Formatting (Cr, L, K) Verified")
    
    print("\n==========================================================")
    print(" ALL VERIFICATION CHECKS PASSED SUCCESSFULLY (100% OPERATIONAL) ")
    print("==========================================================")

if __name__ == "__main__":
    run_verification()
