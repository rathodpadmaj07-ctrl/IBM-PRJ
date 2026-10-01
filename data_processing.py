import pandas as pd
import numpy as np
from typing import Tuple, Dict, List

REQUIRED_COLUMNS = ["urban_zone", "area_sqft", "price"]
OPTIONAL_COLUMNS = ["property_id", "property_type", "bedrooms", "bathrooms"]

def format_currency_inr(val: float, is_difference: bool = False) -> str:
    """
    Format numeric values into Indian currency notation (Cr, L, K).
    Maintains correct numeric representation internally while presenting clean UI text.
    """
    if pd.isna(val) or val is None:
        return "N/A"
    
    is_negative = val < 0
    abs_val = abs(val)
    sign = "-" if is_negative else ("+" if is_difference and val > 0 else "")
    
    if abs_val >= 10000000: # 1 Crore = 10,000,000
        formatted = f"{sign}₹{abs_val / 10000000:.2f} Cr"
    elif abs_val >= 100000: # 1 Lakh = 100,000
        formatted = f"{sign}₹{abs_val / 100000:.2f} L"
    elif abs_val >= 1000: # 1 Thousand = 1,000
        formatted = f"{sign}₹{abs_val / 1000:.1f} K"
    else:
        formatted = f"{sign}₹{abs_val:,.0f}"
        
    return formatted

def validate_and_clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict, List[str]]:
    """
    Validates CSV columns, handles missing values, cleans data types, 
    and filters out non-positive area or price values.
    """
    messages = []
    initial_rows = len(df)
    
    if df.empty:
        return pd.DataFrame(), {"initial_rows": 0, "cleaned_rows": 0, "removed_rows": 0}, ["Uploaded dataset is empty."]
    
    # Standardize column names (lowercase strip)
    df_clean = df.copy()
    df_clean.columns = [str(c).strip().lower() for c in df_clean.columns]
    
    # Map back to standard names if needed
    col_mapping = {
        "urban_zone": "urban_zone", "zone": "urban_zone", "location": "urban_zone",
        "area_sqft": "area_sqft", "area": "area_sqft", "sqft": "area_sqft", "size_sqft": "area_sqft",
        "price": "price", "cost": "price", "amount": "price",
        "property_id": "property_id", "id": "property_id",
        "property_type": "property_type", "type": "property_type",
        "bedrooms": "bedrooms", "beds": "bedrooms", "bhk": "bedrooms",
        "bathrooms": "bathrooms", "baths": "bathrooms"
    }
    
    df_clean = df_clean.rename(columns={c: col_mapping[c] for c in df_clean.columns if c in col_mapping})
    
    # Verify required columns
    missing_req = [col for col in REQUIRED_COLUMNS if col not in df_clean.columns]
    if missing_req:
        return pd.DataFrame(), {"initial_rows": initial_rows, "cleaned_rows": 0, "removed_rows": initial_rows}, [
            f"Missing required columns: {', '.join(missing_req)}. Required columns are: {', '.join(REQUIRED_COLUMNS)}"
        ]
        
    # Handle optional columns
    if "property_id" not in df_clean.columns:
        df_clean["property_id"] = [f"P{1000 + i + 1}" for i in range(len(df_clean))]
        messages.append("Optional column 'property_id' was auto-generated.")
    else:
        df_clean["property_id"] = df_clean["property_id"].astype(str)
        
    if "property_type" not in df_clean.columns:
        df_clean["property_type"] = "Standard"
        messages.append("Optional column 'property_type' set to default 'Standard'.")
        
    if "bedrooms" not in df_clean.columns:
        df_clean["bedrooms"] = np.nan
        
    if "bathrooms" not in df_clean.columns:
        df_clean["bathrooms"] = np.nan
        
    # Numeric conversion
    for num_col in ["area_sqft", "price", "bedrooms", "bathrooms"]:
        if num_col in df_clean.columns:
            df_clean[num_col] = pd.to_numeric(df_clean[num_col], errors="coerce")
            
    # Filter valid rows (price > 0 and area_sqft > 0)
    valid_mask = (df_clean["price"] > 0) & (df_clean["area_sqft"] > 0) & df_clean["urban_zone"].notna()
    df_cleaned = df_clean[valid_mask].copy()
    
    # Strip whitespace from string columns
    df_cleaned["urban_zone"] = df_cleaned["urban_zone"].astype(str).str.strip()
    df_cleaned["property_type"] = df_cleaned["property_type"].astype(str).str.strip()
    
    cleaned_rows = len(df_cleaned)
    removed_rows = initial_rows - cleaned_rows
    
    if removed_rows > 0:
        messages.append(f"Removed {removed_rows} invalid or incomplete rows (missing values, price <= 0, or area <= 0).")
        
    stats_meta = {
        "initial_rows": initial_rows,
        "cleaned_rows": cleaned_rows,
        "removed_rows": removed_rows
    }
    
    return df_cleaned, stats_meta, messages

def calculate_expected_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates Price per sqft, Expected Price based on median price/sqft per urban zone,
    and explicit Price Difference / Price Difference (%) relative to property features.
    
    Explicit Labels:
    - Actual Price
    - Expected Price
    - Price Difference
    - Price Difference (%)
    """
    df_calc = df.copy()
    df_calc["price_per_sqft"] = df_calc["price"] / df_calc["area_sqft"]
    
    # Zone median rate per sqft benchmark
    zone_medians = df_calc.groupby("urban_zone")["price_per_sqft"].median().to_dict()
    df_calc["zone_median_rate_per_sqft"] = df_calc["urban_zone"].map(zone_medians)
    
    # Explicit calculations
    df_calc["Actual Price"] = df_calc["price"]
    df_calc["Expected Price"] = df_calc["zone_median_rate_per_sqft"] * df_calc["area_sqft"]
    df_calc["Price Difference"] = df_calc["Actual Price"] - df_calc["Expected Price"]
    df_calc["Price Difference (%)"] = ((df_calc["Actual Price"] - df_calc["Expected Price"]) / df_calc["Expected Price"]) * 100.0
    
    return df_calc

def get_urban_zone_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes statistical metrics per urban zone.
    """
    if df.empty:
        return pd.DataFrame()
        
    zone_stats = []
    for zone_name, group in df.groupby("urban_zone"):
        prices = group["price"]
        rates = group["price_per_sqft"]
        
        q1 = prices.quantile(0.25)
        q3 = prices.quantile(0.75)
        iqr = q3 - q1
        
        zone_stats.append({
            "Urban Zone": zone_name,
            "Count": len(group),
            "Mean Price": prices.mean(),
            "Median Price": prices.median(),
            "Std Dev Price": prices.std() if len(group) > 1 else 0.0,
            "Min Price": prices.min(),
            "Max Price": prices.max(),
            "Q1 Price": q1,
            "Q3 Price": q3,
            "IQR Price": iqr,
            "Mean Price / Sqft": rates.mean(),
            "Median Price / Sqft": rates.median()
        })
        
    return pd.DataFrame(zone_stats)
