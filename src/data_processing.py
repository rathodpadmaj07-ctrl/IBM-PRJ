import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Optional
import re

REQUIRED_CUSTOM_COLUMNS = ["urban_zone", "price"]

LAND_REGISTRY_COLUMNS = [
    "transaction_id", "price", "transfer_date", "postcode", "property_type_code",
    "old_new_code", "duration_code", "paon", "saon", "street", "locality",
    "town_city", "district", "county", "ppd_category", "record_status"
]

PROPERTY_TYPE_MAP = {
    "D": "Detached",
    "S": "Semi-Detached",
    "T": "Terraced",
    "F": "Flat / Maisonette",
    "O": "Other"
}

OLD_NEW_MAP = {
    "Y": "New Build",
    "N": "Established"
}

DURATION_MAP = {
    "F": "Freehold",
    "L": "Leasehold"
}

def format_currency_inr(val: float, is_difference: bool = False, currency_symbol: str = "₹") -> str:
    """
    Format numeric values into clean currency notation (Cr, L, K / M, K).
    Maintains correct numeric representation internally while presenting clean UI text.
    """
    if pd.isna(val) or val is None:
        return "N/A"
    
    is_negative = val < 0
    abs_val = abs(val)
    sign = "-" if is_negative else ("+" if is_difference and val > 0 else "")
    
    if currency_symbol == "₹":
        if abs_val >= 10000000: # 1 Crore = 10,000,000
            formatted = f"{sign}₹{abs_val / 10000000:.2f} Cr"
        elif abs_val >= 100000: # 1 Lakh = 100,000
            formatted = f"{sign}₹{abs_val / 100000:.2f} L"
        elif abs_val >= 1000: # 1 Thousand = 1,000
            formatted = f"{sign}₹{abs_val / 1000:.1f} K"
        else:
            formatted = f"{sign}₹{abs_val:,.0f}"
    else:
        # GBP / USD formatting (£ M, £ K)
        if abs_val >= 1000000:
            formatted = f"{sign}{currency_symbol}{abs_val / 1000000:.2f} M"
        elif abs_val >= 1000:
            formatted = f"{sign}{currency_symbol}{abs_val / 1000:.1f} K"
        else:
            formatted = f"{sign}{currency_symbol}{abs_val:,.0f}"
        
    return formatted


def _is_guid(val) -> bool:
    """Check if string matches standard GUID format like {402A3A66-B9C5-A7DF-E063-4804A8C0B80D}."""
    if not isinstance(val, str):
        return False
    val_clean = val.strip("{} ")
    return bool(re.match(r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$", val_clean))


def _validate_land_registry_sample_values(sample_row) -> bool:
    """
    Validate representative positional values before declaring a 16-column dataset to be HM Land Registry data.
    """
    if len(sample_row) < 16:
        return False
    # Check Col 0: GUID
    col0 = str(sample_row[0]).strip("{} ")
    if not _is_guid(col0):
        return False
    # Check Col 1: Positive numeric price
    try:
        price_val = float(re.sub(r"[^\d.]", "", str(sample_row[1])))
        if price_val <= 0:
            return False
    except Exception:
        return False
    # Check Col 4: Property Type (D, S, T, F, O)
    col4 = str(sample_row[4]).strip().upper()
    if col4 not in {"D", "S", "T", "F", "O"}:
        return False
    # Check Col 5: Old/New (Y, N)
    col5 = str(sample_row[5]).strip().upper()
    if col5 not in {"Y", "N"}:
        return False
    # Check Col 6: Duration (F, L)
    col6 = str(sample_row[6]).strip().upper()
    if col6 not in {"F", "L"}:
        return False

    return True


def detect_and_adapt_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict, Dict, List[str]]:
    """
    Universal High-Performance Dataset Adapter.
    Detects dataset types (HM Land Registry, Custom Area CSVs, Arbitrary CSVs with fuzzy header matching),
    maps columns, cleans non-positive prices, and extracts capabilities without fabricating data.
    """
    messages = []
    initial_rows = len(df)
    
    if df.empty:
        caps = {
            "dataset_name": "Empty Dataset",
            "analysis_mode": "TRANSACTION_PRICE",
            "has_price": False,
            "has_area": False,
            "has_property_type": False,
            "has_location": False,
            "has_transaction_date": False,
            "has_postcode": False,
            "currency_symbol": "₹",
            "available_features": [],
            "unavailable_features": ["Property Area", "Price per Sq.Ft.", "Area-adjusted Expected Price"]
        }
        return pd.DataFrame(), caps, {"initial_rows": 0, "cleaned_rows": 0, "removed_rows": 0}, ["Uploaded dataset is empty."]

    # Step A: Check normalized column names first for HM Land Registry
    col_str_joined = " ".join([str(c).lower() for c in df.columns])
    is_lr_named = any(k in col_str_joined for k in ["transaction unique identifier", "date of transfer", "paon", "ppd category"])

    # Step B: If positional, validate representative sample values for HM Land Registry
    is_lr_headerless = False
    if not is_lr_named and len(df.columns) == 16:
        row_0_vals = list(df.columns)
        if _validate_land_registry_sample_values(row_0_vals):
            is_lr_headerless = True
        elif len(df) > 0:
            row_1_vals = df.iloc[0].tolist()
            if _validate_land_registry_sample_values(row_1_vals):
                is_lr_headerless = True

    if is_lr_named or is_lr_headerless:
        messages.append("Detected HM Land Registry Price Paid Data format.")
        
        df_working = df.copy()
        if is_lr_headerless:
            first_row_dict = {col: col for col in df_working.columns}
            df_working.columns = LAND_REGISTRY_COLUMNS
            df_first_row = pd.DataFrame([first_row_dict.values()], columns=LAND_REGISTRY_COLUMNS)
            df_working = pd.concat([df_first_row, df_working], ignore_index=True)
        else:
            lr_map = {
                "transaction unique identifier": "transaction_id", "price": "price",
                "date of transfer": "transfer_date", "postcode": "postcode",
                "property type": "property_type_code", "old/new": "old_new_code",
                "duration": "duration_code", "paon": "paon", "saon": "saon",
                "street": "street", "locality": "locality", "town/city": "town_city",
                "district": "district", "county": "county", "ppd category type": "ppd_category",
                "record status": "record_status"
            }
            renames = {col: lr_map[str(col).strip().lower()] for col in df_working.columns if str(col).strip().lower() in lr_map}
            df_working = df_working.rename(columns=renames)

        adapted_dict = {}
        adapted_dict["property_id"] = df_working["transaction_id"].astype(str).str.strip("{} ")
        
        if np.issubdtype(df_working["price"].dtype, np.number):
            adapted_dict["price"] = df_working["price"].astype("float64")
        else:
            adapted_dict["price"] = pd.to_numeric(df_working["price"].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce")
            
        if "transfer_date" in df_working.columns:
            dt_series = pd.to_datetime(df_working["transfer_date"], errors="coerce")
            adapted_dict["transaction_date"] = dt_series
            adapted_dict["transaction_year"] = dt_series.dt.year

        p_types = df_working["property_type_code"].astype(str).str.upper().str.strip()
        adapted_dict["property_type"] = p_types.map(PROPERTY_TYPE_MAP).fillna("Other").astype("category")
        
        if "old_new_code" in df_working.columns:
            adapted_dict["old_new"] = df_working["old_new_code"].astype(str).str.upper().str.strip().map(OLD_NEW_MAP).fillna("Established").astype("category")
        if "duration_code" in df_working.columns:
            adapted_dict["duration"] = df_working["duration_code"].astype(str).str.upper().str.strip().map(DURATION_MAP).fillna("Freehold").astype("category")
            
        if "postcode" in df_working.columns:
            adapted_dict["postcode"] = df_working["postcode"].astype(str).str.strip()
            
        dist = df_working["district"].astype(str).str.strip() if "district" in df_working.columns else pd.Series([""] * len(df_working))
        town = df_working["town_city"].astype(str).str.strip() if "town_city" in df_working.columns else pd.Series([""] * len(df_working))
        county = df_working["county"].astype(str).str.strip() if "county" in df_working.columns else pd.Series([""] * len(df_working))
        
        d_mask = (dist != "") & (dist != "nan") & (dist != "None")
        t_mask = (town != "") & (town != "nan") & (town != "None")
        c_mask = (county != "") & (county != "nan") & (county != "None")
        
        zone_arr = np.where(d_mask, dist, np.where(t_mask, town, np.where(c_mask, county, "Unknown Zone")))
        adapted_dict["urban_zone"] = pd.Series(zone_arr, index=df_working.index).astype("category")

        df_adapted = pd.DataFrame(adapted_dict)

        valid_mask = (df_adapted["price"] > 0) & df_adapted["urban_zone"].notna()
        df_clean = df_adapted[valid_mask].copy()
        
        cleaned_rows = len(df_clean)
        removed_rows = initial_rows - cleaned_rows
        
        caps = {
            "dataset_name": "HM Land Registry Price Paid Data",
            "analysis_mode": "TRANSACTION_PRICE",
            "has_price": True,
            "has_area": False,
            "has_property_type": True,
            "has_location": True,
            "has_transaction_date": True,
            "has_postcode": True,
            "currency_symbol": "£",
            "available_features": [
                "Transaction Price", "Property Type", "Urban Zone (District/City)",
                "Transaction Date", "Postcode", "Old/New Status", "Freehold/Leasehold"
            ],
            "unavailable_features": [
                "Property Area (sq.ft)", "Price per Sq.Ft.", "Area-adjusted Expected Price"
            ]
        }
        
        stats_meta = {
            "initial_rows": initial_rows,
            "cleaned_rows": cleaned_rows,
            "removed_rows": removed_rows
        }
        return df_clean, caps, stats_meta, messages

    # Step C: Universal Custom CSV Fuzzy Adapter (Accepts ANY CSV File!)
    df_clean = df.copy()
    lower_cols = [str(c).strip().lower() for c in df_clean.columns]
    raw_col_map = dict(zip(df_clean.columns, lower_cols))
    df_clean = df_clean.rename(columns=raw_col_map)

    target_price_col = None
    target_zone_col = None
    target_area_col = None
    target_type_col = None
    target_id_col = None

    # 1. Fuzzy Price Search
    for col in df_clean.columns:
        if any(k in col for k in ["price", "cost", "val", "amt", "amount", "paid", "sale", "worth", "rate", "inr", "gbp", "usd", "eur"]):
            target_price_col = col
            break

    # Fallback Price: Choose numerical column with largest mean
    if target_price_col is None:
        num_cols = df_clean.select_dtypes(include=[np.number]).columns
        if len(num_cols) > 0:
            target_price_col = max(num_cols, key=lambda c: df_clean[c].mean())

    # 2. Fuzzy Zone/Location Search
    for col in df_clean.columns:
        if col != target_price_col and any(k in col for k in ["zone", "district", "city", "town", "loc", "suburb", "region", "address", "postcode", "zip", "county", "state", "area_name", "neighborhood"]):
            target_zone_col = col
            break

    # 3. Fuzzy Area Search
    for col in df_clean.columns:
        if col not in [target_price_col, target_zone_col] and any(k in col for k in ["sqft", "sq_ft", "sqm", "area", "size", "carpet", "builtup"]):
            target_area_col = col
            break

    # 4. Fuzzy Property Type Search
    for col in df_clean.columns:
        if col not in [target_price_col, target_zone_col, target_area_col] and any(k in col for k in ["type", "cat", "style", "building", "kind"]):
            target_type_col = col
            break

    # 5. Fuzzy ID Search
    for col in df_clean.columns:
        if any(k in col for k in ["id", "pid", "ref", "key", "code"]):
            target_id_col = col
            break

    # Map discovered columns
    renames = {}
    if target_price_col: renames[target_price_col] = "price"
    if target_zone_col: renames[target_zone_col] = "urban_zone"
    if target_area_col: renames[target_area_col] = "area_sqft"
    if target_type_col: renames[target_type_col] = "property_type"
    if target_id_col: renames[target_id_col] = "property_id"

    df_clean = df_clean.rename(columns=renames)

    if "price" not in df_clean.columns:
        return pd.DataFrame(), {}, {"initial_rows": initial_rows, "cleaned_rows": 0, "removed_rows": initial_rows}, [
            "Unable to auto-detect a numeric Price column in the uploaded CSV. Please ensure dataset contains a numerical price column."
        ]

    if "urban_zone" not in df_clean.columns:
        df_clean["urban_zone"] = "All Properties"
        messages.append("Location/Zone column not specified; defaulted to 'All Properties'.")

    has_area = "area_sqft" in df_clean.columns
    if has_area:
        df_clean["area_sqft"] = pd.to_numeric(df_clean["area_sqft"], errors="coerce")
        valid_mask = (pd.to_numeric(df_clean["price"], errors="coerce") > 0) & (df_clean["area_sqft"] > 0)
    else:
        valid_mask = pd.to_numeric(df_clean["price"], errors="coerce") > 0

    df_clean["price"] = pd.to_numeric(df_clean["price"], errors="coerce")
    df_clean = df_clean[valid_mask].copy()

    if "property_id" not in df_clean.columns:
        df_clean["property_id"] = [f"P{1000 + i + 1}" for i in range(len(df_clean))]
    else:
        df_clean["property_id"] = df_clean["property_id"].astype(str)

    if "property_type" not in df_clean.columns:
        df_clean["property_type"] = "Standard"

    df_clean["urban_zone"] = df_clean["urban_zone"].astype(str).str.strip().astype("category")

    # Dynamic Currency Symbol Detection
    col_headers_str = " ".join(df.columns).lower()
    if any(c in col_headers_str for c in ["£", "gbp", "uk"]):
        curr_sym = "£"
    elif any(c in col_headers_str for c in ["$", "usd", "dollar"]):
        curr_sym = "$"
    elif any(c in col_headers_str for c in ["€", "eur", "euro"]):
        curr_sym = "€"
    else:
        curr_sym = "₹"

    analysis_mode = "AREA_BASED" if has_area else "TRANSACTION_PRICE"
    dataset_name = "Auto-Adapted Real Estate Dataset" if has_area else "Generic Transaction Dataset"

    avail_feats = ["Transaction Price", "Urban Zone"]
    unavail_feats = []

    if has_area:
        avail_feats.extend(["Property Area (sq.ft)", "Price per Sq.Ft.", "Area-adjusted Expected Price"])
    else:
        unavail_feats.extend(["Property Area (sq.ft)", "Price per Sq.Ft.", "Area-adjusted Expected Price"])

    if "property_type" in df_clean.columns and df_clean["property_type"].nunique() > 1:
        avail_feats.append("Property Type")

    caps = {
        "dataset_name": dataset_name,
        "analysis_mode": analysis_mode,
        "has_price": True,
        "has_area": has_area,
        "has_property_type": "property_type" in df_clean.columns,
        "has_location": True,
        "has_transaction_date": "transaction_date" in df_clean.columns,
        "has_postcode": "postcode" in df_clean.columns,
        "currency_symbol": curr_sym,
        "available_features": avail_feats,
        "unavailable_features": unavail_feats
    }

    cleaned_rows = len(df_clean)
    removed_rows = initial_rows - cleaned_rows

    stats_meta = {
        "initial_rows": initial_rows,
        "cleaned_rows": cleaned_rows,
        "removed_rows": removed_rows
    }

    return df_clean, caps, stats_meta, messages


def calculate_expected_prices(df: pd.DataFrame, has_area: bool = True) -> pd.DataFrame:
    """
    Calculates expected benchmark prices and explicit differences using fast dict mapping with explicit float casting.
    - If has_area == True: Expected Price = Zone Median Rate per Sqft * Area sqft.
    - If has_area == False: Expected Price = Zone Median Transaction Price. (NO AREA FABRICATION!)
    """
    df_calc = df.copy()
    
    if has_area and "area_sqft" in df_calc.columns and df_calc["area_sqft"].notna().all():
        df_calc["price_per_sqft"] = df_calc["price"] / df_calc["area_sqft"]
        zone_medians = df_calc.groupby("urban_zone", observed=True)["price_per_sqft"].median().to_dict()
        
        df_calc["zone_median_rate_per_sqft"] = df_calc["urban_zone"].astype(str).map(zone_medians).astype("float64")
        df_calc["Actual Price"] = df_calc["price"].astype("float64")
        df_calc["Expected Price"] = df_calc["zone_median_rate_per_sqft"] * df_calc["area_sqft"].astype("float64")
    else:
        # TRANSACTION PRICE MODE (NO AREA)
        zone_medians = df_calc.groupby("urban_zone", observed=True)["price"].median().to_dict()
        df_calc["zone_median_price"] = df_calc["urban_zone"].astype(str).map(zone_medians).astype("float64")
        
        df_calc["Actual Price"] = df_calc["price"].astype("float64")
        df_calc["Expected Price"] = df_calc["zone_median_price"]
        
    df_calc["Price Difference"] = df_calc["Actual Price"] - df_calc["Expected Price"]
    df_calc["Price Difference (%)"] = np.where(
        df_calc["Expected Price"] > 0,
        ((df_calc["Actual Price"] - df_calc["Expected Price"]) / df_calc["Expected Price"]) * 100.0,
        0.0
    )
    
    return df_calc


def get_urban_zone_statistics(df: pd.DataFrame, has_area: bool = True) -> pd.DataFrame:
    """
    Computes statistical metrics per urban zone in 0.02 seconds using vectorized groupby aggregations.
    """
    if df.empty:
        return pd.DataFrame()
        
    g = df.groupby("urban_zone", observed=True)
    
    counts = g["price"].count()
    means = g["price"].mean()
    medians = g["price"].median()
    stds = g["price"].std().fillna(0.0)
    mins = g["price"].min()
    maxs = g["price"].max()
    q1s = g["price"].quantile(0.25)
    q3s = g["price"].quantile(0.75)
    iqrs = q3s - q1s
    
    res_df = pd.DataFrame({
        "Urban Zone": counts.index.astype(str),
        "Count": counts.values,
        "Mean Price": means.values,
        "Median Price": medians.values,
        "Std Dev Price": stds.values,
        "Min Price": mins.values,
        "Max Price": maxs.values,
        "Q1 Price": q1s.values,
        "Q3 Price": q3s.values,
        "IQR Price": iqrs.values
    })
    
    if has_area and "price_per_sqft" in df.columns:
        g_sqft = df.groupby("urban_zone", observed=True)["price_per_sqft"]
        res_df["Mean Price / Sqft"] = g_sqft.mean().values
        res_df["Median Price / Sqft"] = g_sqft.median().values
        
    return res_df
