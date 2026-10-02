import streamlit as st
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
import io

# Import custom processing, statistical, and visualization modules
from src.data_processing import (
    detect_and_adapt_dataset,
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
    plot_zone_comparison,
    plot_price_by_property_type,
    plot_transaction_timeline
)

# Page Configuration
st.set_page_config(
    page_title="Property Pulse — Real Estate Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Phase 2 & 3 CSS Design System
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
    
    /* Brand Header */
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

    /* Dataset Status Panel */
    .dataset-status-panel {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-blue);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 1.25rem;
    }
    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .panel-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--text-primary);
    }
    .mode-tag {
        background-color: rgba(59, 130, 246, 0.15);
        color: var(--accent-blue);
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .panel-meta-row {
        display: flex;
        gap: 20px;
        font-size: 0.82rem;
        color: var(--text-secondary);
        margin-bottom: 10px;
    }
    .feature-chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 6px;
    }
    .chip-avail {
        background-color: rgba(34, 197, 94, 0.12);
        color: var(--accent-green);
        border: 1px solid rgba(34, 197, 94, 0.25);
        font-size: 0.73rem;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .chip-unavail {
        background-color: rgba(148, 163, 184, 0.1);
        color: var(--text-secondary);
        border: 1px solid rgba(148, 163, 184, 0.2);
        font-size: 0.73rem;
        padding: 2px 8px;
        border-radius: 4px;
        text-decoration: line-through;
    }

    /* Scope Status Chips */
    .scope-chip-container {
        display: flex;
        gap: 8px;
        align-items: center;
        margin-bottom: 1.25rem;
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

    /* Navigation Tabs without Emojis */
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

    /* KPI Cards */
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
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    .kpi-desc {
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    /* Section Header Banners */
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
    
    /* Semantic Badges */
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

    /* Workflow Diagram Cards */
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

    /* Disclaimer Note */
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


@st.cache_data(show_spinner="Analyzing real estate dataset...")
def _cached_load_data(file_bytes_or_path, is_uploaded_bytes: bool = False):
    """
    Cached dataset reader & adapter for fast loading of 160MB+ files.
    """
    if is_uploaded_bytes:
        raw_df = pd.read_csv(io.BytesIO(file_bytes_or_path))
    else:
        raw_df = pd.read_csv(file_bytes_or_path)
    return detect_and_adapt_dataset(raw_df)


def load_data(data_source: str, uploaded_file=None) -> Tuple[pd.DataFrame, Dict, Dict, List[str]]:
    """Loads dataset from sample CSV or uploaded file using robust detection & caching."""
    if data_source == "Upload CSV":
        if uploaded_file is None:
            return pd.DataFrame(), {}, {}, []
        try:
            file_bytes = uploaded_file.getvalue()
            return _cached_load_data(file_bytes, is_uploaded_bytes=True)
        except Exception as e:
            return pd.DataFrame(), {}, {}, [f"Unable to analyze dataset. Error reading CSV file: {str(e)}"]
    else:
        try:
            return _cached_load_data("data/sample_real_estate.csv", is_uploaded_bytes=False)
        except Exception as e:
            return pd.DataFrame(), {}, {}, [f"Error loading sample dataset: {str(e)}"]


def main():
    # ------------------- BRAND SIDEBAR HEADER -------------------
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
                <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:2px;">Supports custom CSV files & HM Land Registry (pp-2025.csv)</div>
                <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:4px;"><b>Auto-detects:</b> Schema, Price, Zone & Area presence</div>
            </div>
            ''', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Choose CSV File", type=["csv"], label_visibility="collapsed")

        df_clean, caps, meta_stats, warnings = load_data(data_source, uploaded_file)

        for msg in warnings:
            st.info(msg)

        if df_clean.empty and data_source == "Upload CSV" and uploaded_file is None:
            st.info("Please choose a CSV file above to execute statistical analysis.")
            return
        elif df_clean.empty:
            st.error("No valid dataset available to analyze.")
            return

        has_area = caps.get("has_area", True)
        currency_sym = caps.get("currency_symbol", "₹")

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
    df_processed = calculate_expected_prices(df_clean, has_area=has_area)
    df_classified = analyze_and_classify_properties(df_processed, alpha=alpha, min_obs=min_obs, has_area=has_area)

    # Active dataset filtering based on scope
    active_df = df_classified.copy()
    if selected_zone != "All Urban Zones":
        active_df = active_df[active_df["urban_zone"] == selected_zone]
    if selected_prop_type != "All Types":
        active_df = active_df[active_df["property_type"] == selected_prop_type]

    if active_df.empty:
        st.warning("No properties match the selected filter criteria.")
        return

    # ------------------- MAIN HEADER & SCOPE STATUS -------------------
    st.markdown('<div class="app-header-title">REAL ESTATE PRICE OUTLIER ANALYZER</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-header-sub">Statistical identification of unusual property pricing across urban zones.</div>', unsafe_allow_html=True)

    # ------------------- DATASET STATUS PANEL -------------------
    mode_text = "MODE 1 — AREA-BASED PROPERTY ANALYSIS" if has_area else "MODE 2 — TRANSACTION PRICE ANALYSIS"
    avail_chips = "".join([f'<span class="chip-avail">✓ {feat}</span>' for feat in caps.get("available_features", [])])
    unavail_chips = "".join([f'<span class="chip-unavail">✗ {feat}</span>' for feat in caps.get("unavailable_features", [])])
    
    cleaned_rows = meta_stats.get("cleaned_rows", len(df_clean))
    removed_rows = meta_stats.get("removed_rows", 0)
    
    st.markdown(f'''
    <div class="dataset-status-panel">
        <div class="panel-header">
            <div class="panel-title">{caps.get("dataset_name", "Real Estate Dataset")}</div>
            <div class="mode-tag">{mode_text}</div>
        </div>
        <div class="panel-meta-row">
            <span><b>Properties Analyzed:</b> {cleaned_rows:,}</span>
            <span><b>Removed/Filtered:</b> {removed_rows:,}</span>
            <span><b>Currency:</b> {currency_sym}</span>
            <span><b>Urban Zones:</b> {df_clean["urban_zone"].nunique():,}</span>
        </div>
        <div class="feature-chip-container">
            {avail_chips}
            {unavail_chips}
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="scope-chip-container">
        <div class="scope-chip">Scope: {selected_zone}</div>
        <div class="scope-chip">Type: {selected_prop_type}</div>
    </div>
    ''', unsafe_allow_html=True)

    # ------------------- NAVIGATION TABS -------------------
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
    # TAB 1: DASHBOARD
    # ==========================================
    with tabs[0]:
        # SECTION 1: EXECUTIVE OVERVIEW (6 KPI Cards)
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
                <div class="kpi-desc">Current scope</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c2:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Average Price</div>
                <div class="kpi-value">{format_currency_inr(avg_price, currency_symbol=currency_sym)}</div>
                <div class="kpi-desc">Mean transaction price</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c3:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Median Price</div>
                <div class="kpi-value">{format_currency_inr(med_price, currency_symbol=currency_sym)}</div>
                <div class="kpi-desc">Typical market price</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c4:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Price Outliers</div>
                <div class="kpi-value" style="color: var(--accent-amber);">{total_outliers:,}</div>
                <div class="kpi-desc">{total_outliers/total_props*100:.1f}% of scope</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c5:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Underpriced</div>
                <div class="kpi-value" style="color: var(--accent-green);">{underpriced_cnt:,}</div>
                <div class="kpi-desc">Potential pricing anomalies</div>
            </div>
            ''', unsafe_allow_html=True)
            
        with c6:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Overpriced</div>
                <div class="kpi-value" style="color: var(--accent-red);">{overpriced_cnt:,}</div>
                <div class="kpi-desc">Potential pricing anomalies</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SECTION 2: MARKET OVERVIEW
        st.markdown('''
        <div class="section-banner">
            <div class="section-banner-title">MARKET OVERVIEW</div>
            <div class="section-banner-sub">Visual analysis of property price distributions and segment relationships across active scope.</div>
        </div>
        ''', unsafe_allow_html=True)

        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            st.plotly_chart(plot_price_distribution(active_df, selected_zone, currency_symbol=currency_sym), use_container_width=True)
        with col_m2:
            if has_area:
                st.plotly_chart(plot_price_vs_area(active_df, selected_zone, currency_symbol=currency_sym), use_container_width=True)
            else:
                type_fig = plot_price_by_property_type(active_df, selected_zone, currency_symbol=currency_sym)
                if type_fig:
                    st.plotly_chart(type_fig, use_container_width=True)
                else:
                    st.plotly_chart(plot_box_plot_by_zone(active_df, selected_zone, currency_symbol=currency_sym), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SECTION 3: OUTLIER SUMMARY
        st.markdown('''
        <div class="section-banner" style="border-left-color: var(--accent-amber);">
            <div class="section-banner-title">OUTLIER SUMMARY</div>
            <div class="section-banner-sub">Distribution of statistical classifications and price variance trends.</div>
        </div>
        ''', unsafe_allow_html=True)

        col_o1, col_o2 = st.columns([1, 1])
        with col_o1:
            st.plotly_chart(plot_classification_breakdown(active_df, selected_zone), use_container_width=True)
        with col_o2:
            if has_area:
                st.plotly_chart(plot_price_per_sqft_distribution(active_df, selected_zone, currency_symbol=currency_sym), use_container_width=True)
            else:
                time_fig = plot_transaction_timeline(active_df, selected_zone, currency_symbol=currency_sym)
                if time_fig:
                    st.plotly_chart(time_fig, use_container_width=True)
                else:
                    st.plotly_chart(plot_box_plot_by_zone(active_df, selected_zone, currency_symbol=currency_sym), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # SECTION 4: KEY FINDINGS
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown("##### KEY FINDINGS")
        
        max_neg_diff = active_df.loc[active_df["Price Difference"].idxmin()]
        max_pos_diff = active_df.loc[active_df["Price Difference"].idxmax()]
        
        findings_html = [
            f'<div class="finding-item"><span class="finding-bullet">•</span> <b>{total_outliers:,}</b> properties were identified as statistical price outliers ({total_outliers/total_props*100:.1f}% of scope).</div>',
            f'<div class="finding-item"><span class="finding-bullet">•</span> <b>{underpriced_cnt:,}</b> properties are classified as <b>Potentially Underpriced</b> (warrant further investigation).</div>',
            f'<div class="finding-item"><span class="finding-bullet">•</span> <b>{overpriced_cnt:,}</b> properties are classified as <b>Potentially Overpriced</b> (warrant valuation review).</div>'
        ]
        
        if has_area and "price_per_sqft" in active_df.columns:
            top_zone_name = active_df.groupby("urban_zone", observed=True)["price_per_sqft"].median().idxmax()
            top_zone_rate = active_df.groupby("urban_zone", observed=True)["price_per_sqft"].median().max()
            findings_html.append(f'<div class="finding-item"><span class="finding-bullet">•</span> <b>{top_zone_name}</b> recorded the highest median price per sq.ft at <b>{currency_sym}{top_zone_rate:,.1f}/sq.ft</b>.</div>')
        else:
            top_zone_name = active_df.groupby("urban_zone", observed=True)["price"].median().idxmax()
            top_zone_price = active_df.groupby("urban_zone", observed=True)["price"].median().max()
            findings_html.append(f'<div class="finding-item"><span class="finding-bullet">•</span> <b>{top_zone_name}</b> recorded the highest median transaction price at <b>{format_currency_inr(top_zone_price, currency_symbol=currency_sym)}</b>.</div>')

        findings_html.append(f'<div class="finding-item"><span class="finding-bullet">•</span> Property <b>{max_pos_diff["property_id"]}</b> ({max_pos_diff["urban_zone"]}) showed the largest positive deviation ({max_pos_diff["Price Difference (%)"]:+.1f}%).</div>')
        findings_html.append(f'<div class="finding-item"><span class="finding-bullet">•</span> Property <b>{max_neg_diff["property_id"]}</b> ({max_neg_diff["urban_zone"]}) showed the largest negative deviation ({max_neg_diff["Price Difference (%)"]:+.1f}%).</div>')
        
        st.markdown("".join(findings_html), unsafe_allow_html=True)
        
        st.markdown('''
        <div class="disclaimer-note">
            <b>Interpretation Note:</b> An outlier indicates an unusual price relative to the selected reference group. It does not by itself establish whether a property is objectively underpriced or overpriced.
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # SECTION 5: PROPERTIES NEEDING INVESTIGATION
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown("##### PROPERTIES NEEDING INVESTIGATION")
        
        investigation_df = active_df[active_df["Classification"] != "Normal"].copy()
        if not investigation_df.empty:
            investigation_df["AbsDiff"] = investigation_df["Price Difference (%)"].abs()
            top_outliers = investigation_df.sort_values(by="AbsDiff", ascending=False).head(5)
            
            disp_inv = pd.DataFrame()
            disp_inv["Property ID"] = top_outliers["property_id"]
            disp_inv["Urban Zone"] = top_outliers["urban_zone"]
            disp_inv["Property Type"] = top_outliers["property_type"]
            disp_inv["Actual Price"] = top_outliers["Actual Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
            disp_inv["Expected Price"] = top_outliers["Expected Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
            disp_inv["Price Difference"] = top_outliers["Price Difference"].apply(lambda x: format_currency_inr(x, is_difference=True, currency_symbol=currency_sym))
            disp_inv["Price Difference (%)"] = top_outliers["Price Difference (%)"].apply(lambda x: f"{x:+.1f}%")
            disp_inv["Classification"] = top_outliers["Classification"]
            
            st.dataframe(disp_inv, use_container_width=True, hide_index=True)
        else:
            st.info("No statistical outliers detected. No properties currently meet the selected outlier criteria.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # TAB 2: DATA EXPLORER
    # ==========================================
    with tabs[1]:
        st.markdown("##### DATASET OVERVIEW")
        st.markdown(f"**{len(active_df):,}** properties &nbsp;|&nbsp; **{len(active_df.columns)}** columns &nbsp;|&nbsp; **{active_df['urban_zone'].nunique():,}** urban zones")

        sort_options = ["price", "urban_zone", "property_type"]
        if has_area:
            sort_options.insert(1, "area_sqft")
            sort_options.insert(2, "price_per_sqft")
            
        col_search1, col_search2 = st.columns([2, 1])
        with col_search1:
            search_query = st.text_input("Search Property ID, Zone, or Postcode:", "", key="explorer_search")
        with col_search2:
            sort_by = st.selectbox("Sort By:", sort_options, index=0)

        explorer_df = active_df.copy()
        if search_query.strip():
            sq = search_query.strip().lower()
            mask = explorer_df["property_id"].astype(str).str.lower().str.contains(sq) | \
                   explorer_df["urban_zone"].astype(str).str.lower().str.contains(sq)
            if "postcode" in explorer_df.columns:
                mask = mask | explorer_df["postcode"].astype(str).str.lower().str.contains(sq)
            explorer_df = explorer_df[mask]
            
        explorer_df = explorer_df.sort_values(by=sort_by, ascending=False)
        
        disp_exp = pd.DataFrame()
        disp_exp["Property ID"] = explorer_df["property_id"]
        disp_exp["Urban Zone"] = explorer_df["urban_zone"]
        disp_exp["Property Type"] = explorer_df["property_type"]
        
        if has_area:
            disp_exp["Area (sq.ft)"] = explorer_df["area_sqft"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
            disp_exp["Price / Sqft"] = explorer_df["price_per_sqft"].apply(lambda x: f"{currency_sym}{x:,.1f}" if pd.notna(x) else "N/A")
            
        disp_exp["Actual Price"] = explorer_df["price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
        
        if "postcode" in explorer_df.columns:
            disp_exp["Postcode"] = explorer_df["postcode"]
        if "transaction_date" in explorer_df.columns:
            disp_exp["Date"] = explorer_df["transaction_date"].dt.strftime("%Y-%m-%d")
            
        disp_exp["Classification"] = explorer_df["Classification"]
        
        st.dataframe(disp_exp, use_container_width=True, hide_index=True)

    # ==========================================
    # TAB 3: ZONE ANALYSIS
    # ==========================================
    with tabs[2]:
        st.markdown("##### URBAN ZONE BENCHMARKING")

        zone_summary = get_urban_zone_statistics(df_classified, has_area=has_area)
        
        if not zone_summary.empty:
            top_med_zone = zone_summary.loc[zone_summary["Median Price"].idxmax()]["Urban Zone"]
            low_med_zone = zone_summary.loc[zone_summary["Median Price"].idxmin()]["Urban Zone"]
            
            z_col1, z_col2, z_col3 = st.columns(3)
            with z_col1:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Highest Median Price Zone</div><div class="kpi-value">{top_med_zone}</div></div>', unsafe_allow_html=True)
            with z_col2:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Lowest Median Price Zone</div><div class="kpi-value">{low_med_zone}</div></div>', unsafe_allow_html=True)
            with z_col3:
                if has_area and "Median Price / Sqft" in zone_summary.columns:
                    top_sqft_zone = zone_summary.loc[zone_summary["Median Price / Sqft"].idxmax()]["Urban Zone"]
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Highest Rate / Sq.Ft Zone</div><div class="kpi-value">{top_sqft_zone}</div></div>', unsafe_allow_html=True)
                else:
                    total_zones = len(zone_summary)
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Urban Zones</div><div class="kpi-value">{total_zones:,}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            disp_zone = zone_summary.copy()
            disp_zone["Mean Price"] = disp_zone["Mean Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
            disp_zone["Median Price"] = disp_zone["Median Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
            disp_zone["Std Dev Price"] = disp_zone["Std Dev Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
            disp_zone["Min Price"] = disp_zone["Min Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
            disp_zone["Max Price"] = disp_zone["Max Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
            disp_zone["Q1 Price"] = disp_zone["Q1 Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
            disp_zone["Q3 Price"] = disp_zone["Q3 Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
            disp_zone["IQR Price"] = disp_zone["IQR Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
            
            if has_area and "Mean Price / Sqft" in disp_zone.columns:
                disp_zone["Mean Price / Sqft"] = disp_zone["Mean Price / Sqft"].apply(lambda x: f"{currency_sym}{x:,.1f}")
                disp_zone["Median Price / Sqft"] = disp_zone["Median Price / Sqft"].apply(lambda x: f"{currency_sym}{x:,.1f}")

            st.dataframe(disp_zone, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(plot_zone_comparison(active_df, selected_zone, currency_symbol=currency_sym, has_area=has_area), use_container_width=True)

    # ==========================================
    # TAB 4: OUTLIER DETECTION
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
            outlier_table_df = outlier_table_df[outlier_table_df["property_id"].astype(str).str.lower().str.contains(sq)]

        disp_outliers = pd.DataFrame()
        disp_outliers["Property ID"] = outlier_table_df["property_id"]
        disp_outliers["Urban Zone"] = outlier_table_df["urban_zone"]
        disp_outliers["Property Type"] = outlier_table_df["property_type"]
        
        if has_area:
            disp_outliers["Area (sq.ft)"] = outlier_table_df["area_sqft"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
            
        disp_outliers["Actual Price"] = outlier_table_df["Actual Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
        disp_outliers["Expected Price"] = outlier_table_df["Expected Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_sym))
        disp_outliers["Price Difference"] = outlier_table_df["Price Difference"].apply(lambda x: format_currency_inr(x, is_difference=True, currency_symbol=currency_sym))
        disp_outliers["Price Difference (%)"] = outlier_table_df["Price Difference (%)"].apply(lambda x: f"{x:+.1f}%")
        disp_outliers["Grubbs Result"] = outlier_table_df["grubbs_result"]
        disp_outliers["IQR Result"] = outlier_table_df["iqr_result"]
        disp_outliers["Classification"] = outlier_table_df["Classification"]

        st.dataframe(disp_outliers, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(plot_outlier_visualization(active_df, selected_zone, currency_symbol=currency_sym, has_area=has_area), use_container_width=True)

    # ==========================================
    # TAB 5: PROPERTY INVESTIGATION
    # ==========================================
    with tabs[4]:
        st.markdown("##### PROPERTY INVESTIGATION")

        prop_list = active_df["property_id"].astype(str).tolist()
        selected_pid = st.selectbox("SELECT PROPERTY:", prop_list, index=0)

        prop_data = active_df[active_df["property_id"].astype(str) == selected_pid].iloc[0]

        actual_p = prop_data["Actual Price"]
        expected_p = prop_data["Expected Price"]
        price_diff = prop_data["Price Difference"]
        price_diff_pct = prop_data["Price Difference (%)"]
        
        zone = prop_data["urban_zone"]
        prop_type = prop_data.get("property_type", "Standard")
        classification = prop_data["Classification"]

        iqr_flag = prop_data["iqr_outlier"]
        iqr_res_text = prop_data["iqr_result"]
        grubbs_flag = prop_data["grubbs_outlier"]
        grubbs_res_text = prop_data["grubbs_result"]

        col_inv1, col_inv2 = st.columns([1, 1])

        with col_inv1:
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            st.markdown(f"### PROPERTY {selected_pid}")
            st.markdown(f"<b>Urban Zone:</b> {zone} &nbsp;|&nbsp; <b>Property Type:</b> {prop_type}")
            st.markdown("<hr style='border-color: var(--border-color); margin:12px 0;'>", unsafe_allow_html=True)
            
            st.markdown("##### PROPERTY ATTRIBUTES")
            if has_area:
                area = prop_data.get("area_sqft", np.nan)
                st.markdown(f"- **Area:** {area:,.0f} sq.ft" if pd.notna(area) else "- **Area:** N/A")
            else:
                st.markdown("- **Floor Area:** Not provided in dataset")
                
            if "bedrooms" in prop_data and pd.notna(prop_data["bedrooms"]):
                st.markdown(f"- **Bedrooms:** {prop_data['bedrooms']}")
            if "bathrooms" in prop_data and pd.notna(prop_data["bathrooms"]):
                st.markdown(f"- **Bathrooms:** {prop_data['bathrooms']}")
            if "postcode" in prop_data and pd.notna(prop_data["postcode"]):
                st.markdown(f"- **Postcode:** {prop_data['postcode']}")
            if "transaction_date" in prop_data and pd.notna(prop_data["transaction_date"]):
                st.markdown(f"- **Transaction Date:** {pd.to_datetime(prop_data['transaction_date']).strftime('%Y-%m-%d')}")
                
            st.markdown("<hr style='border-color: var(--border-color); margin:12px 0;'>", unsafe_allow_html=True)
            
            st.markdown("##### PRICE ANALYSIS")
            st.markdown(f"- **Actual Price:** `{format_currency_inr(actual_p, currency_symbol=currency_sym)}`")
            
            bench_type_label = "Expected Price (Rate × Area):" if has_area else "Expected Price (Zone Median):"
            st.markdown(f"- **{bench_type_label}** `{format_currency_inr(expected_p, currency_symbol=currency_sym)}`")
            st.markdown(f"- **Price Difference:** `{format_currency_inr(price_diff, is_difference=True, currency_symbol=currency_sym)}`")
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
                    f"This property is priced **{abs(price_diff_pct):.1f}% below** the benchmark expected price for **{zone}**.\n\n"
                    "The statistical analysis indicates that it warrants further investigation (e.g., assessing distress sale status, unrecorded title defects, or liquidation urgency)."
                )
            elif classification == "Potentially Overpriced":
                st.markdown(
                    f"This property is priced **{price_diff_pct:+.1f}% above** the benchmark expected price for **{zone}**.\n\n"
                    "The statistical analysis indicates that it requires valuation review (e.g., verifying custom luxury upgrades vs asking price inflation)."
                )
            elif classification == "Statistical Outlier":
                if has_area and "price_per_sqft" in prop_data:
                    rate_str = f"{currency_sym}{prop_data['price_per_sqft']:,.1f}/sq.ft"
                else:
                    rate_str = f"{format_currency_inr(actual_p, currency_symbol=currency_sym)}"
                    
                st.markdown(
                    f"Property **{selected_pid}** was flagged as a statistical outlier with a value of **{rate_str}**.\n\n"
                    "The statistical test indicates that its pricing differs significantly from other properties in its urban zone comparison group."
                )
            else:
                st.markdown(
                    f"Property **{selected_pid}** aligns with expected statistical benchmarks for **{zone}**.\n\n"
                    "No strong statistical evidence of unusual pricing."
                )
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # TAB 6: METHODOLOGY
    # ==========================================
    with tabs[5]:
        st.markdown("##### ACADEMIC STATISTICAL METHODOLOGY")

        st.markdown('''
        <div class="analytics-card">
            <h6>HOW PROPERTY PULSE WORKS</h6>
            <div class="workflow-container">
                <div class="workflow-step"><div class="workflow-num">01</div><div class="workflow-title">Load Dataset</div></div>
                <div class="workflow-step"><div class="workflow-num">02</div><div class="workflow-title">Detect & Adapt Schema</div></div>
                <div class="workflow-step"><div class="workflow-num">03</div><div class="workflow-title">Group by Urban Zone</div></div>
                <div class="workflow-step"><div class="workflow-num">04</div><div class="workflow-title">Benchmark Expected Price</div></div>
                <div class="workflow-step"><div class="workflow-num">05</div><div class="workflow-title">Calculate Price Variance</div></div>
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
            <p><b>Mode 1 (Area-Based):</b> Expected Price = Zone Median Rate per Sq.Ft. × Floor Area</p>
            <p><b>Mode 2 (Transaction Price):</b> Expected Price = Zone Median Transaction Price (No Floor Area Required)</p>
        </div>
        """, unsafe_allow_html=True)

        if has_area:
            st.latex(r"\text{Expected Price} = \text{Median Rate per Sq.Ft.}_{\text{zone}} \times \text{Area}_{\text{sqft}}")
        else:
            st.latex(r"\text{Expected Price} = \text{Median Transaction Price}_{\text{zone}}")

        st.latex(r"\text{Price Difference} = \text{Actual Price} - \text{Expected Price}")
        st.latex(r"\text{Price Difference (\%)} = \frac{\text{Actual Price} - \text{Expected Price}}{\text{Expected Price}} \times 100")

    # ==========================================
    # TAB 7: RESULTS & INSIGHTS
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
                <li><b>Dataset Type:</b> {caps.get("dataset_name", "Real Estate Dataset")}</li>
                <li><b>Analysis Mode:</b> {mode_text}</li>
                <li><b>Properties Analyzed:</b> {n_total:,}</li>
                <li><b>Outliers Found:</b> {n_total_outliers:,} ({n_total_outliers/n_total*100:.1f}%)</li>
                <li><b>Potentially Underpriced:</b> {n_under:,}</li>
                <li><b>Potentially Overpriced:</b> {n_over:,}</li>
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

        zone_summary_df = get_urban_zone_statistics(df_classified, has_area=has_area)
        csv_summary = zone_summary_df.to_csv(index=False).encode('utf-8')
        with col_d3:
            st.download_button("📥 Statistical Summary CSV", csv_summary, "statistical_summary.csv", "text/csv")


if __name__ == "__main__":
    main()
