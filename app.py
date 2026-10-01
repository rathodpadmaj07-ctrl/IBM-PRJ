import streamlit as st
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
import os

# Import custom processing, statistical, and visualization modules
from src.data_processing import (
    validate_and_clean_data,
    calculate_expected_prices,
    get_urban_zone_statistics,
    format_currency_inr
)
from src.statistical_analysis import (
    analyze_and_classify_properties,
    run_grubbs_test,
    run_iqr_analysis,
    run_percentile_analysis
)
from src.visualizations import (
    plot_price_distribution,
    plot_box_plot_by_zone,
    plot_price_vs_area,
    plot_price_per_sqft_distribution,
    plot_classification_breakdown,
    plot_outlier_visualization,
    plot_zone_comparison
)

# Page Configuration (Section 35)
st.set_page_config(
    page_title="Property Pulse — Real Estate Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Phase 2 CSS Design System (Linear/Notion/Stripe Analytics Aesthetic - Section 1, 3, 21, 22)
st.markdown("""
<style>
    :root {
        --bg-main: #0B0F14;
        --bg-secondary: #111720;
        --bg-card: #151D28;
        --border-color: #273242;
        --text-primary: #F5F7FA;
        --text-secondary: #9AA7B5;
        --accent-blue: #3B82F6;
        --accent-green: #22C55E;
        --accent-red: #EF4444;
        --accent-amber: #F59E0B;
        --accent-gray: #94A3B8;
    }

    /* Global Dark App Setup */
    .stApp {
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Sidebar Layout */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    /* Brand Header (Section 2 & 4) */
    .brand-container {
        padding: 0.5rem 0 1rem 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 1rem;
    }
    .sidebar-section-title {
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    /* Main Section Typography */
    .app-header-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 0.15rem;
        letter-spacing: -0.5px;
    }
    .app-header-sub {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-bottom: 1rem;
    }

    /* Scope Status Chips (Section 5) */
    .scope-chip-container {
        display: flex;
        gap: 8px;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    .scope-chip {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.8rem;
        color: var(--accent-blue);
        font-weight: 600;
    }

    /* Navigation Tabs without Emojis (Section 6) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--bg-secondary) !important;
        border-radius: 8px !important;
        padding: 4px !important;
        border: 1px solid var(--border-color) !important;
        gap: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 7px 14px !important;
        border-radius: 6px !important;
        border: none !important;
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--bg-card) !important;
        color: var(--accent-blue) !important;
        border-bottom: 2px solid var(--accent-blue) !important;
        font-weight: 600 !important;
    }

    /* KPI Cards (Section 7) */
    .kpi-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        height: 100%;
    }
    .kpi-label {
        font-size: 0.7rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        font-size: 1.45rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    .kpi-desc {
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    /* Section Header Banners (High Visibility) */
    .section-banner {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-blue);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 20px 0 14px 0;
    }
    .section-banner-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: 0.5px;
    }
    .section-banner-sub {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 2px;
    }

    /* Container Cards */
    .analytics-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    /* Semantic Badges (Section 3 & 24) */
    .badge-underpriced {
        background-color: rgba(34, 197, 94, 0.15);
        color: var(--accent-green);
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-overpriced {
        background-color: rgba(239, 68, 68, 0.15);
        color: var(--accent-red);
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-outlier {
        background-color: rgba(245, 158, 11, 0.15);
        color: var(--accent-amber);
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-normal {
        background-color: rgba(148, 163, 184, 0.15);
        color: var(--accent-gray);
        border: 1px solid rgba(148, 163, 184, 0.3);
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Key Finding Items */
    .finding-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid rgba(39, 50, 66, 0.5);
        font-size: 0.88rem;
        color: var(--text-primary);
    }
    .finding-bullet {
        color: var(--accent-blue);
        font-weight: bold;
    }

    /* Workflow Diagram Cards (Section 15) */
    .workflow-container {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 1rem;
    }
    .workflow-step {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-left: 3px solid var(--accent-blue);
        border-radius: 6px;
        padding: 12px;
        flex: 1 1 200px;
    }
    .workflow-num {
        font-size: 0.75rem;
        font-weight: 800;
        color: var(--accent-blue);
    }
    .workflow-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-top: 4px;
    }

    /* Disclaimer Note (Section 11) */
    .disclaimer-note {
        background-color: rgba(148, 163, 184, 0.05);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: var(--text-secondary);
        margin-top: 12px;
    }

    div[data-testid="stDataFrame"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


def load_data(data_source: str, uploaded_file=None) -> Tuple[pd.DataFrame, Dict, List[str]]:
    """Loads dataset from sample CSV or uploaded file with user-friendly errors (Section 18)."""
    if data_source == "Upload CSV":
        if uploaded_file is None:
            return pd.DataFrame(), {}, []
        try:
            raw_df = pd.read_csv(uploaded_file)
            return validate_and_clean_data(raw_df)
        except Exception as e:
            return pd.DataFrame(), {}, [f"Unable to analyze dataset. Error reading CSV file: {str(e)}"]
    else:
        try:
            raw_df = pd.read_csv("data/sample_real_estate.csv")
            return validate_and_clean_data(raw_df)
        except Exception as e:
            return pd.DataFrame(), {}, [f"Error loading sample dataset: {str(e)}"]


def main():
    # ------------------- BRAND SIDEBAR HEADER (Section 2 & 4) -------------------
    with st.sidebar:
        st.markdown('''
        <div class="brand-container">
            <svg width="200" height="42" viewBox="0 0 200 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M 4,28 L 4,14 L 14,8 L 24,14 L 24,28 Z" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linejoin="round" />
                <path d="M 10,28 L 10,18 L 18,18 L 18,28" fill="none" stroke="#3B82F6" stroke-width="1.5" stroke-linejoin="round" />
                <path d="M 1,22 L 7,22 L 11,16 L 16,25 L 21,11 L 26,17 L 32,17" fill="none" stroke="#22C55E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                <circle cx="21" cy="11" r="2.5" fill="#F59E0B" />
                <text x="40" y="20" font-family="-apple-system, sans-serif" font-weight="800" font-size="14" fill="#F5F7FA" letter-spacing="1">PROPERTY PULSE</text>
                <text x="40" y="32" font-family="-apple-system, sans-serif" font-weight="500" font-size="8.5" fill="#9AA7B5" letter-spacing="0.5">REAL ESTATE ANALYTICS</text>
            </svg>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-title">DATA SOURCE</div>', unsafe_allow_html=True)
        data_source = st.radio(
            "Select Data Source:",
            ["Sample Dataset", "Upload CSV"],
            index=0,
            label_visibility="collapsed"
        )

        uploaded_file = None
        if data_source == "Upload CSV":
            st.markdown('''
            <div style="background-color: var(--bg-card); border:1px solid var(--border-color); border-radius:6px; padding:10px; margin-bottom:10px;">
                <div style="font-weight:700; font-size:0.85rem; color:var(--text-primary);">Upload Dataset</div>
                <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:2px;">CSV files up to 200 MB</div>
                <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:4px;"><b>Required columns:</b> Property ID, Urban Zone, Property Type, Area, Price</div>
            </div>
            ''', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Choose CSV File", type=["csv"], label_visibility="collapsed")

        df_clean, meta_stats, warnings = load_data(data_source, uploaded_file)

        for msg in warnings:
            st.warning(msg)

        if df_clean.empty and data_source == "Upload CSV" and uploaded_file is None:
            st.info("Please choose a CSV file above to execute statistical analysis.")
            return
        elif df_clean.empty:
            st.error("No valid dataset available to analyze.")
            return

        if data_source == "Upload CSV" and not df_clean.empty:
            st.markdown(f'<div style="font-size:0.78rem; color:var(--accent-green); font-weight:600; margin-bottom:10px;">✓ Dataset loaded successfully ({len(df_clean)} properties, {len(df_clean.columns)} columns)</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-title">ANALYSIS SCOPE</div>', unsafe_allow_html=True)

        available_zones = ["All Urban Zones"] + sorted(df_clean["urban_zone"].unique().tolist())
        selected_zone = st.selectbox("Urban Zone:", available_zones, index=0)

        selected_prop_type = "All Types"
        if "property_type" in df_clean.columns and df_clean["property_type"].nunique() > 1:
            types_list = ["All Types"] + sorted(df_clean["property_type"].dropna().unique().tolist())
            selected_prop_type = st.selectbox("Property Type:", types_list, index=0)

        st.markdown('<div class="sidebar-section-title">STATISTICAL SETTINGS</div>', unsafe_allow_html=True)

        min_obs = st.slider(
            "Minimum Observations:",
            min_value=3, max_value=30, value=10, step=1,
            help="Minimum properties required per zone for Grubbs' test."
        )

        alpha = st.selectbox(
            "Significance Level (α):",
            options=[0.01, 0.05, 0.10],
            index=1,
            help="Alpha significance level for hypothesis testing."
        )

        st.markdown("<br><hr style='border-color: var(--border-color);'><div style='font-size:0.7rem; color:var(--text-secondary); text-align:center;'>Statistical Real Estate Analysis Engine</div>", unsafe_allow_html=True)

    # ------------------- CORE STATISTICAL COMPUTATION -------------------
    df_processed = calculate_expected_prices(df_clean)
    df_classified = analyze_and_classify_properties(df_processed, alpha=alpha, min_obs=min_obs)

    # Active dataset filtering based on scope
    active_df = df_classified.copy()
    if selected_zone != "All Urban Zones":
        active_df = active_df[active_df["urban_zone"] == selected_zone]
    if selected_prop_type != "All Types":
        active_df = active_df[active_df["property_type"] == selected_prop_type]

    if active_df.empty:
        st.warning("No properties match the selected filter criteria.")
        return

    # ------------------- MAIN HEADER & SCOPE STATUS CHIPS (Section 5) -------------------
    st.markdown('<div class="app-header-title">REAL ESTATE PRICE OUTLIER ANALYZER</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-header-sub">Statistical identification of unusual property pricing across urban zones.</div>', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="scope-chip-container">
        <div class="scope-chip">Scope: {selected_zone}</div>
        <div class="scope-chip">Type: {selected_prop_type}</div>
    </div>
    ''', unsafe_allow_html=True)

    # ------------------- NAVIGATION TABS WITHOUT EMOJIS (Section 6) -------------------
    tabs = st.tabs([
        "Dashboard",
        "Data Explorer",
        "Zone Analysis",
        "Outlier Detection",
        "Property Investigation",
        "Methodology",
        "Results & Insights"
    ])

    # ==========================================
    # TAB 1: DASHBOARD (Section 7, 8, 9, 10, 16, 17)
    # ==========================================
    with tabs[0]:
        # SECTION 1: EXECUTIVE OVERVIEW (6 KPI Cards - Section 7)
        c1, c2, c3, c4, c5, c6 = st.columns(6)

        total_props = len(active_df)
        avg_price = active_df["price"].mean()
        med_price = active_df["price"].median()

        underpriced_cnt = len(active_df[active_df["Classification"] == "Potentially Underpriced"])
        overpriced_cnt = len(active_df[active_df["Classification"] == "Potentially Overpriced"])
        outlier_cnt = len(active_df[active_df["Classification"] == "Statistical Outlier"])
        total_outliers = underpriced_cnt + overpriced_cnt + outlier_cnt

        with c1:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Total Properties</div>
                <div class="kpi-value">{total_props:,}</div>
                <div class="kpi-desc">Current dataset</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c2:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Average Price</div>
                <div class="kpi-value">{format_currency_inr(avg_price)}</div>
                <div class="kpi-desc">Mean property price</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c3:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Median Price</div>
                <div class="kpi-value">{format_currency_inr(med_price)}</div>
                <div class="kpi-desc">Typical market price</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c4:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Price Outliers</div>
                <div class="kpi-value" style="color: var(--accent-amber);">{total_outliers}</div>
                <div class="kpi-desc">{total_outliers/total_props*100:.1f}% of properties</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c5:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Underpriced</div>
                <div class="kpi-value" style="color: var(--accent-green);">{underpriced_cnt}</div>
                <div class="kpi-desc">Potential pricing anomalies</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c6:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Overpriced</div>
                <div class="kpi-value" style="color: var(--accent-red);">{overpriced_cnt}</div>
                <div class="kpi-desc">Potential pricing anomalies</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SECTION 2: MARKET OVERVIEW (PROMINENT HIGH-VISIBILITY SECTION HEADER)
        st.markdown('''
        <div class="section-banner">
            <div class="section-banner-title">MARKET OVERVIEW</div>
            <div class="section-banner-sub">Visual analysis of property price distributions and floor area relationships across active scope.</div>
        </div>
        ''', unsafe_allow_html=True)

        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            st.plotly_chart(plot_price_distribution(active_df, selected_zone), use_container_width=True)
        with col_m2:
            st.plotly_chart(plot_price_vs_area(active_df, selected_zone), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SECTION 3: OUTLIER SUMMARY (PROMINENT SECTION HEADER)
        st.markdown('''
        <div class="section-banner" style="border-left-color: var(--accent-amber);">
            <div class="section-banner-title">OUTLIER SUMMARY</div>
            <div class="section-banner-sub">Distribution of statistical classification and per-unit area pricing variance.</div>
        </div>
        ''', unsafe_allow_html=True)

        col_o1, col_o2 = st.columns([1, 1])
        with col_o1:
            st.plotly_chart(plot_classification_breakdown(active_df, selected_zone), use_container_width=True)
        with col_o2:
            st.plotly_chart(plot_price_per_sqft_distribution(active_df, selected_zone), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SECTION 4: KEY FINDINGS (Section 14 & 16)
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown("##### KEY FINDINGS")
        
        top_zone_name = active_df.groupby("urban_zone")["price_per_sqft"].median().idxmax()
        top_zone_rate = active_df.groupby("urban_zone")["price_per_sqft"].median().max()
        max_neg_diff = active_df.loc[active_df["Price Difference"].idxmin()]
        max_pos_diff = active_df.loc[active_df["Price Difference"].idxmax()]
        
        st.markdown(f'''
        <div class="finding-item"><span class="finding-bullet">•</span> <b>{total_outliers}</b> properties were identified as statistical price outliers ({total_outliers/total_props*100:.1f}% of dataset).</div>
        <div class="finding-item"><span class="finding-bullet">•</span> <b>{underpriced_cnt}</b> properties are classified as <b>Potentially Underpriced</b> (warrant further investigation).</div>
        <div class="finding-item"><span class="finding-bullet">•</span> <b>{overpriced_cnt}</b> properties are classified as <b>Potentially Overpriced</b> (warrant valuation review).</div>
        <div class="finding-item"><span class="finding-bullet">•</span> <b>{top_zone_name}</b> recorded the highest median price per sq.ft at <b>₹{top_zone_rate:,.1f}/sq.ft</b>.</div>
        <div class="finding-item"><span class="finding-bullet">•</span> Property <b>{max_pos_diff['property_id']}</b> ({max_pos_diff['urban_zone']}) showed the largest positive deviation ({max_pos_diff['Price Difference (%)']:+.1f}%).</div>
        <div class="finding-item"><span class="finding-bullet">•</span> Property <b>{max_neg_diff['property_id']}</b> ({max_neg_diff['urban_zone']}) showed the largest negative deviation ({max_neg_diff['Price Difference (%)']:+.1f}%).</div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="disclaimer-note">
            <b>Interpretation Note:</b> An outlier indicates an unusual price relative to the selected reference group. It does not by itself establish whether a property is objectively underpriced or overpriced.
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # SECTION 5: PROPERTIES NEEDING INVESTIGATION (Section 17)
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown("##### PROPERTIES NEEDING INVESTIGATION")
        
        investigation_df = active_df[active_df["Classification"] != "Normal"].copy()
        if not investigation_df.empty:
            investigation_df["AbsDiff"] = investigation_df["Price Difference (%)"].abs()
            top_outliers = investigation_df.sort_values(by="AbsDiff", ascending=False).head(5)
            
            disp_inv = pd.DataFrame()
            disp_inv["Property ID"] = top_outliers["property_id"]
            disp_inv["Urban Zone"] = top_outliers["urban_zone"]
            disp_inv["Actual Price"] = top_outliers["Actual Price"].apply(format_currency_inr)
            disp_inv["Expected Price"] = top_outliers["Expected Price"].apply(format_currency_inr)
            disp_inv["Price Difference"] = top_outliers["Price Difference"].apply(lambda x: format_currency_inr(x, is_difference=True))
            disp_inv["Price Difference (%)"] = top_outliers["Price Difference (%)"].apply(lambda x: f"{x:+.1f}%")
            disp_inv["Classification"] = top_outliers["Classification"]
            
            st.dataframe(disp_inv, use_container_width=True, hide_index=True)
        else:
            st.info("No statistical outliers detected. No properties currently meet the selected outlier criteria.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # TAB 2: DATA EXPLORER (Section 20)
    # ==========================================
    with tabs[1]:
        st.markdown("##### DATASET OVERVIEW")
        st.markdown(f"**{len(active_df)}** properties &nbsp;|&nbsp; **{len(active_df.columns)}** columns &nbsp;|&nbsp; **{active_df['urban_zone'].nunique()}** urban zones")

        col_search1, col_search2 = st.columns([2, 1])
        with col_search1:
            search_query = st.text_input("Search Property ID or Zone:", "", key="explorer_search")
        with col_search2:
            sort_by = st.selectbox("Sort By:", ["price", "area_sqft", "price_per_sqft"], index=0)

        explorer_df = active_df.copy()
        if search_query.strip():
            sq = search_query.strip().lower()
            explorer_df = explorer_df[
                explorer_df["property_id"].str.lower().str.contains(sq) |
                explorer_df["urban_zone"].str.lower().str.contains(sq)
            ]
            
        explorer_df = explorer_df.sort_values(by=sort_by, ascending=False)
        
        disp_exp = pd.DataFrame()
        disp_exp["Property ID"] = explorer_df["property_id"]
        disp_exp["Urban Zone"] = explorer_df["urban_zone"]
        disp_exp["Property Type"] = explorer_df["property_type"]
        disp_exp["Area (sq.ft)"] = explorer_df["area_sqft"].apply(lambda x: f"{x:,.0f}")
        disp_exp["Actual Price"] = explorer_df["price"].apply(format_currency_inr)
        disp_exp["Price / Sqft"] = explorer_df["price_per_sqft"].apply(lambda x: f"₹{x:,.1f}")
        disp_exp["Classification"] = explorer_df["Classification"]
        
        st.dataframe(disp_exp, use_container_width=True, hide_index=True)

    # ==========================================
    # TAB 3: ZONE ANALYSIS (Section 22)
    # ==========================================
    with tabs[2]:
        st.markdown("##### URBAN ZONE BENCHMARKING")

        zone_summary = get_urban_zone_statistics(df_classified)
        
        if not zone_summary.empty:
            top_med_zone = zone_summary.loc[zone_summary["Median Price"].idxmax()]["Urban Zone"]
            low_med_zone = zone_summary.loc[zone_summary["Median Price"].idxmin()]["Urban Zone"]
            top_sqft_zone = zone_summary.loc[zone_summary["Median Price / Sqft"].idxmax()]["Urban Zone"]
            
            z_col1, z_col2, z_col3 = st.columns(3)
            with z_col1:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Highest Median Price</div><div class="kpi-value">{top_med_zone}</div></div>', unsafe_allow_html=True)
            with z_col2:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Lowest Median Price</div><div class="kpi-value">{low_med_zone}</div></div>', unsafe_allow_html=True)
            with z_col3:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Highest Rate / Sq.Ft</div><div class="kpi-value">{top_sqft_zone}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            disp_zone = zone_summary.copy()
            disp_zone["Mean Price"] = disp_zone["Mean Price"].apply(format_currency_inr)
            disp_zone["Median Price"] = disp_zone["Median Price"].apply(format_currency_inr)
            disp_zone["Std Dev Price"] = disp_zone["Std Dev Price"].apply(format_currency_inr)
            disp_zone["Min Price"] = disp_zone["Min Price"].apply(format_currency_inr)
            disp_zone["Max Price"] = disp_zone["Max Price"].apply(format_currency_inr)
            disp_zone["Q1 Price"] = disp_zone["Q1 Price"].apply(format_currency_inr)
            disp_zone["Q3 Price"] = disp_zone["Q3 Price"].apply(format_currency_inr)
            disp_zone["IQR Price"] = disp_zone["IQR Price"].apply(format_currency_inr)
            disp_zone["Mean Price / Sqft"] = disp_zone["Mean Price / Sqft"].apply(lambda x: f"₹{x:,.1f}")
            disp_zone["Median Price / Sqft"] = disp_zone["Median Price / Sqft"].apply(lambda x: f"₹{x:,.1f}")

            st.dataframe(disp_zone, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(plot_zone_comparison(active_df, selected_zone), use_container_width=True)

    # ==========================================
    # TAB 4: OUTLIER DETECTION (Section 21)
    # ==========================================
    with tabs[3]:
        st.markdown("##### OUTLIER DETECTION")
        st.markdown("<div style='font-size:0.85rem; color:var(--text-secondary); margin-bottom:1rem;'>Properties identified as statistically unusual relative to localized urban zone features.</div>", unsafe_allow_html=True)

        col_of1, col_of2 = st.columns([1, 2])
        with col_of1:
            class_filter = st.selectbox(
                "Filter Category:",
                ["All Outliers & Anomalies", "All Properties", "Potentially Underpriced", "Potentially Overpriced", "Statistical Outlier", "Normal"],
                key="outlier_tab_filter"
            )
        with col_of2:
            outlier_search = st.text_input("Search Property ID:", "", key="outlier_search")

        outlier_table_df = active_df.copy()

        if class_filter == "All Outliers & Anomalies":
            outlier_table_df = outlier_table_df[outlier_table_df["Classification"] != "Normal"]
        elif class_filter != "All Properties":
            outlier_table_df = outlier_table_df[outlier_table_df["Classification"] == class_filter]

        if outlier_search.strip():
            sq = outlier_search.strip().lower()
            outlier_table_df = outlier_table_df[outlier_table_df["property_id"].str.lower().str.contains(sq)]

        disp_outliers = pd.DataFrame()
        disp_outliers["Property ID"] = outlier_table_df["property_id"]
        disp_outliers["Urban Zone"] = outlier_table_df["urban_zone"]
        disp_outliers["Area (sq.ft)"] = outlier_table_df["area_sqft"].apply(lambda x: f"{x:,.0f}")
        disp_outliers["Actual Price"] = outlier_table_df["Actual Price"].apply(format_currency_inr)
        disp_outliers["Expected Price"] = outlier_table_df["Expected Price"].apply(format_currency_inr)
        disp_outliers["Price Difference"] = outlier_table_df["Price Difference"].apply(lambda x: format_currency_inr(x, is_difference=True))
        disp_outliers["Price Difference (%)"] = outlier_table_df["Price Difference (%)"].apply(lambda x: f"{x:+.1f}%")
        disp_outliers["Grubbs Result"] = outlier_table_df["grubbs_result"]
        disp_outliers["IQR Result"] = outlier_table_df["iqr_result"]
        disp_outliers["Classification"] = outlier_table_df["Classification"]

        st.dataframe(disp_outliers, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(plot_outlier_visualization(active_df, selected_zone), use_container_width=True)

    # ==========================================
    # TAB 5: PROPERTY INVESTIGATION (Section 12 & 18)
    # ==========================================
    with tabs[4]:
        st.markdown("##### PROPERTY INVESTIGATION")

        prop_list = active_df["property_id"].tolist()
        default_idx = prop_list.index("P1023") if "P1023" in prop_list else 0
        selected_pid = st.selectbox("SELECT PROPERTY:", prop_list, index=default_idx)

        prop_data = active_df[active_df["property_id"] == selected_pid].iloc[0]

        actual_p = prop_data["Actual Price"]
        expected_p = prop_data["Expected Price"]
        price_diff = prop_data["Price Difference"]
        price_diff_pct = prop_data["Price Difference (%)"]
        
        zone = prop_data["urban_zone"]
        area = prop_data["area_sqft"]
        beds = prop_data.get("bedrooms", "N/A")
        baths = prop_data.get("bathrooms", "N/A")
        classification = prop_data["Classification"]

        iqr_flag = prop_data["iqr_outlier"]
        iqr_res_text = prop_data["iqr_result"]
        grubbs_flag = prop_data["grubbs_outlier"]
        grubbs_res_text = prop_data["grubbs_result"]

        col_inv1, col_inv2 = st.columns([1, 1])

        with col_inv1:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            st.markdown(f"### PROPERTY {selected_pid}")
            st.markdown(f"<b>Urban Zone:</b> {zone}")
            st.markdown("<hr style='border-color: var(--border-color); margin:12px 0;'>", unsafe_allow_html=True)
            
            st.markdown("##### PROPERTY SUMMARY")
            st.markdown(f"- **Area:** {area:,.0f} sq.ft")
            if pd.notna(beds):
                st.markdown(f"- **Bedrooms:** {int(beds) if isinstance(beds, (int, float)) else beds}")
            if pd.notna(baths):
                st.markdown(f"- **Bathrooms:** {int(baths) if isinstance(baths, (int, float)) else baths}")
                
            st.markdown("<hr style='border-color: var(--border-color); margin:12px 0;'>", unsafe_allow_html=True)
            
            st.markdown("##### PRICE ANALYSIS")
            st.markdown(f"- **Actual Price:** `{format_currency_inr(actual_p)}`")
            st.markdown(f"- **Expected Price:** `{format_currency_inr(expected_p)}`")
            st.markdown(f"- **Price Difference:** `{format_currency_inr(price_diff, is_difference=True)}`")
            st.markdown(f"- **Price Difference (%):** `{price_diff_pct:+.1f}%`")
            
            st.markdown("<hr style='border-color: var(--border-color); margin:12px 0;'>", unsafe_allow_html=True)
            st.markdown("##### STATISTICAL EVIDENCE")
            iqr_sym = "✓" if iqr_flag else "✗"
            grubbs_sym = "✓" if grubbs_flag else "✗"
            st.markdown(f"{iqr_sym} **IQR Analysis:** {iqr_res_text}")
            st.markdown(f"{grubbs_sym} **Grubbs' Test:** {grubbs_res_text}")
            
            st.markdown("<hr style='border-color: var(--border-color); margin:12px 0;'>", unsafe_allow_html=True)
            st.markdown("##### CLASSIFICATION")
            if classification == "Potentially Underpriced":
                st.markdown('<span class="badge-underpriced">POTENTIALLY UNDERPRICED</span>', unsafe_allow_html=True)
            elif classification == "Potentially Overpriced":
                st.markdown('<span class="badge-overpriced">POTENTIALLY OVERPRICED</span>', unsafe_allow_html=True)
            elif classification == "Statistical Outlier":
                st.markdown('<span class="badge-outlier">STATISTICAL OUTLIER</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-normal">NORMAL</span>', unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)

        with col_inv2:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            st.markdown("##### PLAIN-ENGLISH INTERPRETATION")

            if classification == "Potentially Underpriced":
                st.markdown(
                    f"This property is priced **{abs(price_diff_pct):.1f}% below** the expected reference price for **{zone}**.\n\n"
                    "The statistical analysis indicates that it warrants further investigation (e.g., assessing distress sale status, unrecorded title defects, or liquidation urgency)."
                )
            elif classification == "Potentially Overpriced":
                st.markdown(
                    f"This property is priced **{price_diff_pct:+.1f}% above** the expected reference price for **{zone}**.\n\n"
                    "The statistical analysis indicates that it requires valuation review (e.g., verifying custom luxury upgrades vs asking price inflation)."
                )
            elif classification == "Statistical Outlier":
                st.markdown(
                    f"Property **{selected_pid}** was flagged as a statistical outlier with a rate of **₹{prop_data['price_per_sqft']:,.1f}/sq.ft**.\n\n"
                    "The statistical test indicates that its price per unit area differs significantly from other properties in its urban zone comparison group."
                )
            else:
                st.markdown(
                    f"Property **{selected_pid}** aligns with expected statistical benchmarks for **{zone}**.\n\n"
                    "No strong statistical evidence of unusual pricing."
                )
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # TAB 6: METHODOLOGY (Section 15 & 16)
    # ==========================================
    with tabs[5]:
        st.markdown("##### ACADEMIC STATISTICAL METHODOLOGY")

        st.markdown('''
        <div class="analytics-card">
            <h6>HOW PROPERTY PULSE WORKS</h6>
            <div class="workflow-container">
                <div class="workflow-step"><div class="workflow-num">01</div><div class="workflow-title">Load Dataset</div></div>
                <div class="workflow-step"><div class="workflow-num">02</div><div class="workflow-title">Clean & Validate</div></div>
                <div class="workflow-step"><div class="workflow-num">03</div><div class="workflow-title">Group by Zone</div></div>
                <div class="workflow-step"><div class="workflow-num">04</div><div class="workflow-title">Estimate Expected Price</div></div>
                <div class="workflow-step"><div class="workflow-num">05</div><div class="workflow-title">Calculate Price Difference</div></div>
                <div class="workflow-step"><div class="workflow-num">06</div><div class="workflow-title">Apply Outlier Detection</div></div>
                <div class="workflow-step"><div class="workflow-num">07</div><div class="workflow-title">Classify Properties</div></div>
                <div class="workflow-step"><div class="workflow-num">08</div><div class="workflow-title">Investigate Outliers</div></div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("""
        <div class="analytics-card">
            <h6>GRUBBS' TEST</h6>
            <p><b>Purpose:</b> Detect an extreme observation in a normally distributed sample.</p>
            <p><b>Interpretation:</b> A statistically significant result suggests the observation is unusually distant from the sample mean.</p>
            <p><b>G-Statistic:</b></p>
        </div>
        """, unsafe_allow_html=True)

        st.latex(r"G = \frac{\max_{i=1..N} |x_i - \bar{x}|}{s}")
        st.latex(r"G_{\text{crit}} = \frac{N - 1}{\sqrt{N}} \sqrt{\frac{t_{\alpha/(2N), N-2}^2}{N - 2 + t_{\alpha/(2N), N-2}^2}}")

        st.markdown("""
        <div class="analytics-card">
            <h6>IQR ANALYSIS</h6>
            <p><b>Purpose:</b> Non-parametric quartile bounds for extreme value identification independent of distribution shape.</p>
            <p><b>Interpretation:</b> Identifies values lying outside 1.5×IQR from Q1/Q3.</p>
            <ul>
                <li><b>IQR</b> = Q3 - Q1</li>
                <li><b>Lower Bound</b> = Q1 - 1.5 × IQR</li>
                <li><b>Upper Bound</b> = Q3 + 1.5 × IQR</li>
            </ul>
        </div>
        
        <div class="analytics-card">
            <h6>EXPECTED PRICE BENCHMARKING</h6>
            <p><b>Purpose:</b> Feature-adjusted reference pricing calculation.</p>
        </div>
        """, unsafe_allow_html=True)

        st.latex(r"\text{Expected Price} = \text{Median Rate per Sq.Ft.}_{\text{zone}} \times \text{Area}_{\text{sqft}}")
        st.latex(r"\text{Price Difference} = \text{Actual Price} - \text{Expected Price}")
        st.latex(r"\text{Price Difference (\%)} = \frac{\text{Actual Price} - \text{Expected Price}}{\text{Expected Price}} \times 100")

    # ==========================================
    # TAB 7: RESULTS & INSIGHTS (Section 17)
    # ==========================================
    with tabs[6]:
        st.markdown("##### ANALYSIS SUMMARY")

        n_total = len(df_classified)
        n_under = len(df_classified[df_classified["Classification"] == "Potentially Underpriced"])
        n_over = len(df_classified[df_classified["Classification"] == "Potentially Overpriced"])
        n_stat = len(df_classified[df_classified["Classification"] == "Statistical Outlier"])
        n_total_outliers = n_under + n_over + n_stat

        st.markdown(f"""
        <div class="analytics-card">
            <h6>DATASET & OUTLIER SUMMARY</h6>
            <ul>
                <li><b>Properties Analyzed:</b> {n_total:,}</li>
                <li><b>Outliers Found:</b> {n_total_outliers} ({n_total_outliers/n_total*100:.1f}%)</li>
                <li><b>Potentially Underpriced:</b> {n_under}</li>
                <li><b>Potentially Overpriced:</b> {n_over}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="analytics-card">
            <h6>LIMITATIONS & METHODOLOGICAL NOTES</h6>
            <ul>
                <li>Statistical price outliers require further investigation to determine physical or market causes.</li>
                <li>An outlier is not automatically evidence of an incorrect, fraudulent, or damaged property listing price.</li>
                <li>Results depend directly on dataset quality, sample size, and localized reference-group selection.</li>
                <li>Grubbs' test assumes univariate normality within each comparison group.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### EXPORT STATISTICAL DATA")

        col_d1, col_d2, col_d3 = st.columns(3)

        csv_cleaned = df_clean.to_csv(index=False).encode('utf-8')
        with col_d1:
            st.download_button("📥 Cleaned Dataset CSV", csv_cleaned, "cleaned_real_estate_data.csv", "text/csv")

        csv_outliers = df_classified.to_csv(index=False).encode('utf-8')
        with col_d2:
            st.download_button("📥 Outlier Results CSV", csv_outliers, "real_estate_outlier_results.csv", "text/csv")

        zone_summary_df = get_urban_zone_statistics(df_classified)
        csv_summary = zone_summary_df.to_csv(index=False).encode('utf-8')
        with col_d3:
            st.download_button("📥 Statistical Summary CSV", csv_summary, "statistical_summary.csv", "text/csv")


if __name__ == "__main__":
    main()
