import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, Tuple, List

def run_grubbs_test(series: pd.Series, alpha: float = 0.05, min_obs: int = 10) -> Dict[str, Any]:
    """
    Performs two-sided Grubbs' Test (Maximum Normed Residual Test) for outliers.
    
    H0: There are no outliers in the dataset.
    H1: There is at least one outlier in the dataset.
    
    Formula:
    G = max(|x_i - mean|) / std
    G_crit = ((N - 1) / sqrt(N)) * sqrt( t_crit^2 / (N - 2 + t_crit^2) )
    where t_crit is t_(alpha / 2N, N - 2)
    """
    clean_s = series.dropna()
    N = len(clean_s)
    
    if N < min_obs:
        return {
            "status": "Insufficient Observations",
            "message": f"Insufficient observations for reliable Grubbs' test (N={N} < min_obs={min_obs}).",
            "is_outlier": False,
            "G_statistic": None,
            "G_critical": None,
            "p_value": None,
            "outlier_index": None,
            "outlier_value": None,
            "outlier_type": None
        }
        
    mean = clean_s.mean()
    std = clean_s.std(ddof=1)
    
    if std == 0 or np.isnan(std):
        return {
            "status": "Zero Variance",
            "message": "Standard deviation is zero; all values in group are identical.",
            "is_outlier": False,
            "G_statistic": 0.0,
            "G_critical": None,
            "p_value": 1.0,
            "outlier_index": None,
            "outlier_value": None,
            "outlier_type": None
        }
        
    abs_diffs = (clean_s - mean).abs()
    max_diff_idx = abs_diffs.idxmax()
    max_val = clean_s.loc[max_diff_idx]
    
    G_stat = abs(max_val - mean) / std
    
    # Critical value of t-distribution at alpha / (2 * N) with df = N - 2
    t_crit = stats.t.ppf(1 - alpha / (2 * N), df=N - 2)
    G_crit = ((N - 1) / np.sqrt(N)) * np.sqrt(t_crit**2 / (N - 2 + t_crit**2))
    
    # Calculate approximate two-tailed p-value for Grubbs' test
    # t_val corresponding to G_stat
    try:
        t_squared = (N * (N - 2) * (G_stat**2)) / ((N - 1)**2 - N * (G_stat**2))
        if t_squared > 0:
            t_val = np.sqrt(t_squared)
            p_val = min(1.0, 2 * N * stats.t.sf(t_val, df=N - 2))
        else:
            p_val = 1.0
    except Exception:
        p_val = 1.0 if G_stat < G_crit else 0.001
        
    is_outlier = bool(G_stat > G_crit)
    outlier_type = "Potentially Overpriced" if max_val > mean else "Potentially Underpriced"
    
    return {
        "status": "Evaluated",
        "message": f"Grubbs' Test evaluated (N={N}, Alpha={alpha}). " +
                   (f"Flagged extreme observation at index {max_diff_idx}." if is_outlier else "No significant single extreme outlier found."),
        "is_outlier": is_outlier,
        "G_statistic": float(G_stat),
        "G_critical": float(G_crit),
        "p_value": float(p_val),
        "outlier_index": max_diff_idx,
        "outlier_value": float(max_val),
        "outlier_type": outlier_type if is_outlier else "Normal",
        "mean": float(mean),
        "std": float(std),
        "sample_size": N
    }

def run_iqr_analysis(series: pd.Series) -> Dict[str, Any]:
    """
    Computes Interquartile Range (IQR) and upper/lower bounds.
    Lower Bound = Q1 - 1.5 * IQR
    Upper Bound = Q3 + 1.5 * IQR
    """
    clean_s = series.dropna()
    if len(clean_s) < 4:
        return {
            "Q1": None, "Q3": None, "IQR": None,
            "lower_bound": None, "upper_bound": None,
            "lower_outliers": [], "upper_outliers": []
        }
        
    q1 = clean_s.quantile(0.25)
    q3 = clean_s.quantile(0.75)
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    lower_outliers = clean_s[clean_s < lower_bound].index.tolist()
    upper_outliers = clean_s[clean_s > upper_bound].index.tolist()
    
    return {
        "Q1": float(q1),
        "Q3": float(q3),
        "IQR": float(iqr),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "lower_outliers": lower_outliers,
        "upper_outliers": upper_outliers
    }

def run_percentile_analysis(series: pd.Series, lower_p: float = 5.0, upper_p: float = 95.0) -> Dict[str, Any]:
    """
    Calculates 5th and 95th percentile bounds for distribution tail assessment.
    """
    clean_s = series.dropna()
    p_low = clean_s.quantile(lower_p / 100.0)
    p_high = clean_s.quantile(upper_p / 100.0)
    
    return {
        "p_low_percentile": lower_p,
        "p_high_percentile": upper_p,
        "p_low_value": float(p_low),
        "p_high_value": float(p_high),
        "lower_tail_indices": clean_s[clean_s < p_low].index.tolist(),
        "upper_tail_indices": clean_s[clean_s > p_high].index.tolist()
    }

def analyze_and_classify_properties(
    df: pd.DataFrame, 
    alpha: float = 0.05, 
    min_obs: int = 10
) -> pd.DataFrame:
    """
    Applies Grubbs' Test, IQR Method, and Percentile Analysis within each Urban Zone
    and classifies every property into:
    - Potentially Underpriced
    - Potentially Overpriced
    - Statistical Outlier
    - Normal
    """
    df_result = df.copy()
    
    # Initialize flags
    df_result["grubbs_outlier"] = False
    df_result["grubbs_result"] = "Normal"
    df_result["iqr_outlier"] = False
    df_result["iqr_result"] = "Normal"
    df_result["iqr_bound_type"] = "Within IQR Bounds"
    df_result["percentile_tail"] = "Middle 90%"
    df_result["Classification"] = "Normal"
    
    # Process zone by zone
    for zone_name, group_indices in df_result.groupby("urban_zone").groups.items():
        sub_df = df_result.loc[group_indices]
        
        # 1. IQR Analysis on price_per_sqft within zone
        iqr_res = run_iqr_analysis(sub_df["price_per_sqft"])
        if iqr_res["lower_bound"] is not None:
            l_bound = iqr_res["lower_bound"]
            u_bound = iqr_res["upper_bound"]
            
            for idx in group_indices:
                rate = df_result.loc[idx, "price_per_sqft"]
                if rate < l_bound:
                    df_result.loc[idx, "iqr_outlier"] = True
                    df_result.loc[idx, "iqr_result"] = "Below Lower Bound"
                    df_result.loc[idx, "iqr_bound_type"] = "Lower Bound Outlier"
                elif rate > u_bound:
                    df_result.loc[idx, "iqr_outlier"] = True
                    df_result.loc[idx, "iqr_result"] = "Above Upper Bound"
                    df_result.loc[idx, "iqr_bound_type"] = "Upper Bound Outlier"
                    
        # 2. Grubbs' Test on price_per_sqft within zone
        grubbs_res = run_grubbs_test(sub_df["price_per_sqft"], alpha=alpha, min_obs=min_obs)
        if grubbs_res["is_outlier"] and grubbs_res["outlier_index"] is not None:
            out_idx = grubbs_res["outlier_index"]
            df_result.loc[out_idx, "grubbs_outlier"] = True
            df_result.loc[out_idx, "grubbs_result"] = f"Flagged ({grubbs_res['outlier_type']})"
        elif grubbs_res["status"] == "Insufficient Observations":
            for idx in group_indices:
                df_result.loc[idx, "grubbs_result"] = "Insufficient Obs"
                
        # 3. Percentile Analysis on price_per_sqft
        pct_res = run_percentile_analysis(sub_df["price_per_sqft"])
        for idx in group_indices:
            rate = df_result.loc[idx, "price_per_sqft"]
            if rate < pct_res["p_low_value"]:
                df_result.loc[idx, "percentile_tail"] = "Lower 5th Percentile"
            elif rate > pct_res["p_high_value"]:
                df_result.loc[idx, "percentile_tail"] = "Upper 95th Percentile"
                
    # 4. Final Classification Logic based on statistical findings and explicit price difference %
    for idx in df_result.index:
        p_diff_pct = df_result.loc[idx, "Price Difference (%)"]
        iqr_flag = df_result.loc[idx, "iqr_outlier"]
        grubbs_flag = df_result.loc[idx, "grubbs_outlier"]
        iqr_res_str = df_result.loc[idx, "iqr_result"]
        
        # Classification criteria
        if (iqr_res_str == "Below Lower Bound" or p_diff_pct < -15.0) and (iqr_flag or grubbs_flag or p_diff_pct < -18.0):
            df_result.loc[idx, "Classification"] = "Potentially Underpriced"
        elif (iqr_res_str == "Above Upper Bound" or p_diff_pct > 15.0) and (iqr_flag or grubbs_flag or p_diff_pct > 18.0):
            df_result.loc[idx, "Classification"] = "Potentially Overpriced"
        elif iqr_flag or grubbs_flag:
            df_result.loc[idx, "Classification"] = "Statistical Outlier"
        else:
            df_result.loc[idx, "Classification"] = "Normal"
            
    return df_result
