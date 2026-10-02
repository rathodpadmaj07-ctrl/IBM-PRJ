import os
import sys
import pandas as pd
import numpy as np
import time

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_flush(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

from src.data_processing import detect_and_adapt_dataset, calculate_expected_prices, get_urban_zone_statistics, format_currency_inr
from src.statistical_analysis import analyze_and_classify_properties, run_grubbs_test, run_iqr_analysis
from src.visualizations import (
    plot_price_distribution, plot_box_plot_by_zone, plot_price_vs_area,
    plot_price_per_sqft_distribution, plot_classification_breakdown,
    plot_outlier_visualization, plot_zone_comparison,
    plot_price_by_property_type, plot_transaction_timeline
)

def test_dataset(file_path, label):
    print_flush(f"\n==================================================")
    print_flush(f" TESTING DATASET: {label}")
    print_flush(f" File path: {file_path}")
    print_flush(f"==================================================")
    
    if not os.path.exists(file_path):
        print_flush(f"[ERROR] File does not exist at {file_path}")
        return False
        
    t_start = time.time()
    try:
        df_raw = pd.read_csv(file_path, engine="pyarrow")
    except Exception:
        df_raw = pd.read_csv(file_path)
    t_read = time.time() - t_start
    print_flush(f"[OK] Read CSV (PyArrow/C Engine): {len(df_raw):,} rows, {len(df_raw.columns)} cols in {t_read:.3f}s")
    
    # 1. Dataset Detection & Adaptation
    t_adapt_start = time.time()
    df_clean, caps, meta, msgs = detect_and_adapt_dataset(df_raw)
    t_adapt = time.time() - t_adapt_start
    
    print_flush(f"[OK] Adapted in {t_adapt:.3f}s:")
    print_flush(f"  Detected Dataset Type: {caps['dataset_name']}")
    print_flush(f"  Analysis Mode: {caps['analysis_mode']}")
    print_flush(f"  Cleaned Rows: {meta['cleaned_rows']:,}")
    print_flush(f"  Removed Rows: {meta['removed_rows']:,}")
    print_flush(f"  Cleaned Columns: {len(df_clean.columns)}")
    print_flush(f"  Has Area: {caps['has_area']}")
    print_flush(f"  Currency Symbol: {caps['currency_symbol']}")
    print_flush(f"  Available Features: {caps['available_features']}")
    print_flush(f"  Unavailable Features: {caps['unavailable_features']}")
    for m in msgs:
        print_flush(f"  Message: {m}")
        
    assert not df_clean.empty, "Cleaned dataset should not be empty!"
    assert "price" in df_clean.columns, "price column missing!"
    assert "urban_zone" in df_clean.columns, "urban_zone column missing!"
    
    # Strict NO AREA FABRICATION check for HM Land Registry
    if "Land Registry" in caps["dataset_name"]:
        assert caps["has_area"] == False, "HM Land Registry MUST NOT have has_area=True!"
        assert "area_sqft" not in df_clean.columns, "HM Land Registry MUST NOT create area_sqft!"
        assert "price_per_sqft" not in df_clean.columns, "HM Land Registry MUST NOT compute price_per_sqft!"
        print_flush("[OK] Verified strict NO AREA FABRICATION rule for HM Land Registry!")
        
    # 2. Benchmark Calculation
    t_bench_start = time.time()
    df_processed = calculate_expected_prices(df_clean, has_area=caps["has_area"])
    t_bench = time.time() - t_bench_start
    print_flush(f"[OK] Calculated expected prices in {t_bench:.3f}s. Avg Price Diff: {df_processed['Price Difference'].mean():.2f}")
    
    # 3. Statistical Analysis
    t_stat_start = time.time()
    df_classified = analyze_and_classify_properties(df_processed, alpha=0.05, min_obs=10, has_area=caps["has_area"])
    t_stat = time.time() - t_stat_start
    print_flush(f"[OK] Executed statistical classification in {t_stat:.3f}s.")
    print_flush("  Classifications Summary:", df_classified["Classification"].value_counts().to_dict())
    
    # 4. Urban Zone Statistics
    t_zone_start = time.time()
    zone_stats = get_urban_zone_statistics(df_classified, has_area=caps["has_area"])
    t_zone = time.time() - t_zone_start
    print_flush(f"[OK] Zone statistics computed for {len(zone_stats)} zones in {t_zone:.3f}s.")
    
    # 5. Visualizations
    t_vis_start = time.time()
    fig1 = plot_price_distribution(df_classified, currency_symbol=caps["currency_symbol"])
    fig2 = plot_classification_breakdown(df_classified)
    fig3 = plot_outlier_visualization(df_classified, currency_symbol=caps["currency_symbol"], has_area=caps["has_area"])
    fig4 = plot_zone_comparison(df_classified, currency_symbol=caps["currency_symbol"], has_area=caps["has_area"])
    t_vis = time.time() - t_vis_start
    print_flush(f"[OK] Core visualizations created in {t_vis:.3f}s.")
    
    if caps["has_area"]:
        fig_area = plot_price_vs_area(df_classified, currency_symbol=caps["currency_symbol"])
        fig_sqft = plot_price_per_sqft_distribution(df_classified, currency_symbol=caps["currency_symbol"])
        print_flush("[OK] Area-based plots (Scatter & Violin) created.")
    else:
        fig_type = plot_price_by_property_type(df_classified, currency_symbol=caps["currency_symbol"])
        fig_time = plot_transaction_timeline(df_classified, currency_symbol=caps["currency_symbol"])
        print_flush(f"[OK] Transaction-mode plots created (Property Type Box: {fig_type is not None}, Timeline: {fig_time is not None}).")
        
    t_total = time.time() - t_start
    print_flush(f"[SUCCESS] Total processing time for {label}: {t_total:.3f}s")
    return True


if __name__ == "__main__":
    print_flush("==================================================")
    print_flush(" STARTING PROPERTY PULSE COMPREHENSIVE SUITE TEST")
    print_flush("==================================================")
    
    test_dataset("data/sample_real_estate.csv", "Sample Real Estate Dataset (Area-Based)")
    test_dataset("data/custom_area_sample.csv", "Custom Area-Based Dataset")
    
    lr_file = r"C:\Users\Padmaj Rathod\Downloads\pp-2025.csv"
    if os.path.exists(lr_file):
        test_dataset(lr_file, "HM Land Registry pp-2025.csv (Transaction Price Mode)")
    else:
        print_flush(f"[INFO] Skipping HM Land Registry test as file was not found at {lr_file}")
        
    print_flush("\n==================================================")
    print_flush(" 🎉 ALL COMPREHENSIVE PIPELINE TESTS COMPLETED!")
    print_flush("==================================================")
