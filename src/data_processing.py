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
    Robust Dataset Adapter Layer with strict detection priority.
    1. First inspect normalized column names for recognizable Land Registry headers.
    2. If headers match, use name-based mapping.
    3. If 16 columns and positional values pass multi-point sample validation (GUID, Price, Type, Old/New, Duration), use positional mapping.
    4. Otherwise, handle as custom/standard dataset.
    Never fabricates missing floor area.
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

    # Step A: Check normalized column names first
    col_str_joined = " ".join([str(c).lower() for c in df.columns])
    is_lr_named = any(k in col_str_joined for k in ["transaction unique identifier", "date of transfer", "paon", "ppd category"])

    # Step B: If positional, validate representative sample values
    is_lr_headerless = False
    if not is_lr_named and len(df.columns) == 16:
        # Sample row 0 (which pandas took as header) or first row of data
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
            renames = {}
            for col in df_working.columns:
                c_low = str(col).strip().lower()
                if c_low in lr_map:
                    renames[col] = lr_map[c_low]
            df_working = df_working.rename(columns=renames)

        # Process Land Registry Fields into adapted internal DataFrame
        df_adapted = pd.DataFrame()
        df_adapted["property_id"] = df_working["transaction_id"].astype(str).str.strip("{} ")
        df_adapted["price"] = pd.to_numeric(df_working["price"].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce")
        
        if "transfer_date" in df_working.columns:
            df_adapted["transaction_date"] = pd.to_datetime(df_working["transfer_date"], errors="coerce")
            df_adapted["transaction_year"] = df_adapted["transaction_date"].dt.year
        else:
            df_adapted["transaction_date"] = pd.NaT
            df_adapted["transaction_year"] = np.nan

        p_types = df_working["property_type_code"].astype(str).str.upper().str.strip()
        df_adapted["property_type"] = p_types.map(PROPERTY_TYPE_MAP).fillna("Other")
        
        if "old_new_code" in df_working.columns:
            df_adapted["old_new"] = df_working["old_new_code"].astype(str).str.upper().str.strip().map(OLD_NEW_MAP).fillna("Established")
        if "duration_code" in df_working.columns:
            df_adapted["duration"] = df_working["duration_code"].astype(str).str.upper().str.strip().map(DURATION_MAP).fillna("Freehold")
            
        if "postcode" in df_working.columns:
            df_adapted["postcode"] = df_working["postcode"].astype(str).str.strip()
            
        if "town_city" in df_working.columns:
            df_adapted["town_city"] = df_working["town_city"].astype(str).str.strip()
        if "district" in df_working.columns:
            df_adapted["district"] = df_working["district"].astype(str).str.strip()
        if "county" in df_working.columns:
            df_adapted["county"] = df_working["county"].astype(str).str.strip()
            
        # Determine Urban Zone from District -> Town/City -> County
        district_series = df_adapted["district"] if "district" in df_adapted.columns else pd.Series([""] * len(df_adapted))
        town_series = df_adapted["town_city"] if "town_city" in df_adapted.columns else pd.Series([""] * len(df_adapted))
        county_series = df_adapted["county"] if "county" in df_adapted.columns else pd.Series([""] * len(df_adapted))
        
        zone_series = district_series.replace(["nan", "None", ""], np.nan)
        zone_series = zone_series.fillna(town_series.replace(["nan", "None", ""], np.nan))
        zone_series = zone_series.fillna(county_series.replace(["nan", "None", ""], np.nan))
        df_adapted["urban_zone"] = zone_series.fillna("Unknown Zone")
        
        # Convert string categories to categorical dtype for RAM efficiency
        for cat_col in ["urban_zone", "property_type", "old_new", "duration"]:
            if cat_col in df_adapted.columns:
                df_adapted[cat_col] = df_adapted[cat_col].astype("category")

        # Clean valid rows
        valid_mask = (df_adapted["price"] > 0) & df_adapted["urban_zone"].notna()
        df_clean = df_adapted[valid_mask].copy()
        
        cleaned_rows = len(df_clean)
        removed_rows = initial_rows - cleaned_rows
        
        caps = {
            "dataset_name": "HM Land Registry Price Paid Data",
            "analysis_mode": "TRANSACTION_PRICE",
            "has_price": True,
            "has_area": False, # STRICTLY FALSE
            "has_property_type": True,
            "has_location": True,
            "has_transaction_date": True,
            "has_postcode": True,
            "currency_symbol": "£", # UK GBP for HM Land Registry
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

    # Step C: Standard Custom / Property Pulse Dataset (with or without Area)
    df_clean = df.copy()
    df_clean.columns = [str(c).strip().lower() for c in df_clean.columns]
    
    col_mapping = {
        "urban_zone": "urban_zone", "zone": "urban_zone", "location": "urban_zone", "district": "urban_zone", "city": "urban_zone",
        "area_sqft": "area_sqft", "area": "area_sqft", "sqft": "area_sqft", "size_sqft": "area_sqft", "size": "area_sqft",
        "price": "price", "cost": "price", "amount": "price", "value": "price",
        "property_id": "property_id", "id": "property_id", "transaction_id": "property_id",
        "property_type": "property_type", "type": "property_type",
        "bedrooms": "bedrooms", "beds": "bedrooms", "bhk": "bedrooms",
        "bathrooms": "bathrooms", "baths": "bathrooms",
        "date": "transaction_date", "transaction_date": "transaction_date"
    }
    
    df_clean = df_clean.rename(columns={c: col_mapping[c] for c in df_clean.columns if c in col_mapping})
    
    if "price" not in df_clean.columns:
        return pd.DataFrame(), {}, {"initial_rows": initial_rows, "cleaned_rows": 0, "removed_rows": initial_rows}, [
            "Missing required column: 'price'. Please upload a dataset containing price information."
        ]
        
    if "urban_zone" not in df_clean.columns:
        df_clean["urban_zone"] = "All Properties"
        messages.append("Location column missing; defaulted to 'All Properties'.")

    # Determine Area availability
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
        
    df_clean["urban_zone"] = df_clean["urban_zone"].astype(str).str.strip()
    
    analysis_mode = "AREA_BASED" if has_area else "TRANSACTION_PRICE"
    dataset_name = "Property Pulse Custom Dataset" if has_area else "Generic Transaction Dataset"
    
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
        "currency_symbol": "₹",
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
    Calculates expected benchmark prices and explicit differences.
    - If has_area == True: Expected Price = Zone Median Rate per Sqft * Area sqft.
    - If has_area == False: Expected Price = Zone Median Transaction Price. (NO AREA FABRICATION!)
    """
    df_calc = df.copy()
    
    if has_area and "area_sqft" in df_calc.columns and df_calc["area_sqft"].notna().all():
        df_calc["price_per_sqft"] = df_calc["price"] / df_calc["area_sqft"]
        zone_medians = df_calc.groupby("urban_zone", observed=True)["price_per_sqft"].median().to_dict()
        df_calc["zone_median_rate_per_sqft"] = df_calc["urban_zone"].map(zone_medians)
        
        df_calc["Actual Price"] = df_calc["price"]
        df_calc["Expected Price"] = df_calc["zone_median_rate_per_sqft"] * df_calc["area_sqft"]
    else:
        # TRANSACTION PRICE MODE (NO AREA)
        zone_medians = df_calc.groupby("urban_zone", observed=True)["price"].median().to_dict()
        df_calc["zone_median_price"] = df_calc["urban_zone"].map(zone_medians)
        
        df_calc["Actual Price"] = df_calc["price"]
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
    Computes statistical metrics per urban zone.
    """
    if df.empty:
        return pd.DataFrame()
        
    zone_stats = []
    for zone_name, group in df.groupby("urban_zone", observed=True):
        prices = group["price"]
        q1 = prices.quantile(0.25)
        q3 = prices.quantile(0.75)
        iqr = q3 - q1
        
        stat_item = {
            "Urban Zone": str(zone_name),
            "Count": len(group),
            "Mean Price": prices.mean(),
            "Median Price": prices.median(),
            "Std Dev Price": prices.std() if len(group) > 1 else 0.0,
            "Min Price": prices.min(),
            "Max Price": prices.max(),
            "Q1 Price": q1,
            "Q3 Price": q3,
            "IQR Price": iqr
        }
        
        if has_area and "price_per_sqft" in group.columns:
            rates = group["price_per_sqft"]
            stat_item["Mean Price / Sqft"] = rates.mean()
            stat_item["Median Price / Sqft"] = rates.median()
            
        zone_stats.append(stat_item)
        
    return pd.DataFrame(zone_stats)
