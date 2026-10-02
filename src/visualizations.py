import plotly.express as px
import plotly.graph_objects as gg
import pandas as pd
import numpy as np
from src.data_processing import format_currency_inr

# Phase 2 Design System Palette
COLOR_MAP = {
    "Normal": "#94A3B8",                # Neutral slate gray
    "Potentially Underpriced": "#22C55E", # Emerald green
    "Potentially Overpriced": "#EF4444",  # Red
    "Statistical Outlier": "#F59E0B"     # Amber yellow
}

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#151D28",
    font=dict(color="#F5F7FA", family="-apple-system, BlinkMacSystemFont, sans-serif"),
    title_font=dict(color="#F5F7FA", size=15),
    legend=dict(font=dict(color="#F5F7FA", size=11), bgcolor="rgba(21, 29, 40, 0.85)"),
    margin=dict(l=40, r=40, t=50, b=40)
)

def _apply_dark_style(fig, xaxis_title="", yaxis_title="", height=450):
    fig.update_layout(
        **DARK_LAYOUT,
        height=height
    )
    fig.update_xaxes(
        title=dict(text=f"<b>{xaxis_title}</b>", font=dict(color="#F5F7FA", size=12)),
        gridcolor="#273242",
        zerolinecolor="#273242",
        tickfont=dict(color="#F5F7FA", size=11)
    )
    fig.update_yaxes(
        title=dict(text=f"<b>{yaxis_title}</b>", font=dict(color="#F5F7FA", size=12)),
        gridcolor="#273242",
        zerolinecolor="#273242",
        tickfont=dict(color="#F5F7FA", size=11)
    )
    return fig

def _sample_for_plotting(df: pd.DataFrame, max_normals: int = 5000) -> pd.DataFrame:
    """
    Ultra-fast plotting sampler:
    Retains 100% of statistical outliers and samples normal properties to prevent UI lag on 1M+ rows.
    """
    if len(df) <= max_normals * 2:
        return df
        
    outliers = df[df["Classification"] != "Normal"]
    normals = df[df["Classification"] == "Normal"]
    
    if len(normals) > max_normals:
        normals = normals.sample(n=max_normals, random_state=42)
        
    return pd.concat([outliers, normals]).sort_index()


def plot_price_distribution(df: pd.DataFrame, selected_zone: str = "All Urban Zones", currency_symbol: str = "₹"):
    """
    Clean histogram of property prices with Mean and Median reference lines.
    """
    df_plot = _sample_for_plotting(df)
    title_text = "Property Price Distribution" if selected_zone == "All Urban Zones" else f"Property Price Distribution — {selected_zone}"
    
    hover_opts = ["property_id", "urban_zone"]
    if "property_type" in df_plot.columns:
        hover_opts.append("property_type")
    if "area_sqft" in df_plot.columns:
        hover_opts.append("area_sqft")

    fig = px.histogram(
        df_plot,
        x="price",
        color="urban_zone" if selected_zone == "All Urban Zones" else "Classification",
        color_discrete_map=COLOR_MAP if selected_zone != "All Urban Zones" else None,
        nbins=35,
        title=f"<b>{title_text}</b>",
        labels={"price": f"Property Price ({currency_symbol})", "urban_zone": "Urban Zone"},
        hover_data=hover_opts,
        template="plotly_dark",
        opacity=0.85
    )
    
    fig.update_traces(marker=dict(line=dict(color="#151D28", width=1)))
    
    mean_val = df["price"].mean()
    median_val = df["price"].median()
    
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="#3B82F6",
        line_width=2.5,
        annotation_text=f"<b>Mean: {format_currency_inr(mean_val, currency_symbol=currency_symbol)}</b>",
        annotation_font_color="#3B82F6",
        annotation_position="top left"
    )
    fig.add_vline(
        x=median_val,
        line_dash="dot",
        line_color="#22C55E",
        line_width=2.5,
        annotation_text=f"<b>Median: {format_currency_inr(median_val, currency_symbol=currency_symbol)}</b>",
        annotation_font_color="#22C55E",
        annotation_position="top right"
    )
    
    return _apply_dark_style(fig, xaxis_title=f"Property Price ({currency_symbol})", yaxis_title="Count", height=450)

def plot_box_plot_by_zone(df: pd.DataFrame, selected_zone: str = "All Urban Zones", currency_symbol: str = "₹"):
    """
    Box plot showing price distribution and extreme observations per urban zone.
    """
    df_plot = _sample_for_plotting(df)
    title_text = "Price Distribution & Outliers by Urban Zone" if selected_zone == "All Urban Zones" else f"Price Variance & Outliers — {selected_zone}"
    
    hover_cols = ["property_id"]
    if "area_sqft" in df_plot.columns:
        hover_cols.append("area_sqft")
        
    fig = px.box(
        df_plot,
        x="urban_zone" if selected_zone == "All Urban Zones" else "property_type",
        y="price",
        color="urban_zone" if selected_zone == "All Urban Zones" else "property_type",
        points="outliers",
        title=f"<b>{title_text}</b>",
        labels={"price": f"Property Price ({currency_symbol})", "urban_zone": "Urban Zone", "property_type": "Property Type"},
        hover_data=hover_cols,
        template="plotly_dark"
    )
    
    x_label = "Urban Zone" if selected_zone == "All Urban Zones" else "Property Type"
    return _apply_dark_style(fig, xaxis_title=x_label, yaxis_title=f"Property Price ({currency_symbol})", height=450)

def plot_price_vs_area(df: pd.DataFrame, selected_zone: str = "All Urban Zones", currency_symbol: str = "₹"):
    """
    Scatter plot of Price vs Area. (Only used when has_area=True).
    """
    if "area_sqft" not in df.columns:
        return None
        
    df_plot = _sample_for_plotting(df).copy()
    title_text = "Property Price vs. Area (sq.ft)" if selected_zone == "All Urban Zones" else f"Property Price vs. Area (sq.ft) — {selected_zone}"
    
    df_plot["hover_actual_price"] = df_plot["Actual Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_symbol))
    df_plot["hover_expected_price"] = df_plot["Expected Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_symbol))
    df_plot["hover_price_diff"] = df_plot["Price Difference"].apply(lambda x: format_currency_inr(x, is_difference=True, currency_symbol=currency_symbol))
    df_plot["hover_price_diff_pct"] = df_plot["Price Difference (%)"].apply(lambda x: f"{x:+.1f}%")
    
    hover_cols = ["property_id", "urban_zone", "area_sqft", "hover_actual_price", "hover_expected_price", "hover_price_diff", "hover_price_diff_pct"]
    if "bedrooms" in df_plot.columns and df_plot["bedrooms"].notna().any():
        hover_cols.append("bedrooms")

    fig = px.scatter(
        df_plot,
        x="area_sqft",
        y="price",
        color="Classification",
        color_discrete_map=COLOR_MAP,
        size="area_sqft",
        size_max=14,
        opacity=0.85,
        hover_name="property_id",
        custom_data=hover_cols,
        title=f"<b>{title_text}</b>",
        template="plotly_dark"
    )
    
    fig.update_traces(marker=dict(line=dict(width=1, color="#0B0F14")))
    
    hovertemplate = (
        "<b>Property ID:</b> %{customdata[0]}<br>" +
        "<b>Urban Zone:</b> %{customdata[1]}<br>" +
        "<b>Area:</b> %{customdata[2]:,.0f} sq.ft<br>" +
        "<b>Actual Price:</b> %{customdata[3]}<br>" +
        "<b>Expected Price:</b> %{customdata[4]}<br>" +
        "<b>Price Difference:</b> %{customdata[5]}<br>" +
        "<b>Price Difference (%):</b> %{customdata[6]}<br>"
    )
    if "bedrooms" in hover_cols:
        hovertemplate += "<b>Bedrooms:</b> %{customdata[7]}<br>"
        
    hovertemplate += "<extra></extra>"
    fig.update_traces(hovertemplate=hovertemplate)
    
    return _apply_dark_style(fig, xaxis_title="Area (sq.ft)", yaxis_title=f"Property Price ({currency_symbol})", height=450)

def plot_price_per_sqft_distribution(df: pd.DataFrame, selected_zone: str = "All Urban Zones", currency_symbol: str = "₹"):
    """
    Violin chart of Price per Square Foot by Urban Zone. (Only used when has_area=True).
    """
    if "price_per_sqft" not in df.columns:
        return None
        
    df_plot = _sample_for_plotting(df)
    title_text = "Price per Sq.Ft. by Urban Zone" if selected_zone == "All Urban Zones" else f"Price per Sq.Ft. — {selected_zone}"
    
    fig = px.violin(
        df_plot,
        x="urban_zone" if selected_zone == "All Urban Zones" else "property_type",
        y="price_per_sqft",
        color="urban_zone" if selected_zone == "All Urban Zones" else "property_type",
        box=True,
        points="outliers",
        title=f"<b>{title_text}</b>",
        labels={"price_per_sqft": f"Price / Sq.Ft ({currency_symbol})", "urban_zone": "Urban Zone", "property_type": "Property Type"},
        hover_data=["property_id", "price"],
        template="plotly_dark"
    )
    
    x_label = "Urban Zone" if selected_zone == "All Urban Zones" else "Property Type"
    return _apply_dark_style(fig, xaxis_title=x_label, yaxis_title=f"Price per Sq.Ft ({currency_symbol})", height=420)

def plot_classification_breakdown(df: pd.DataFrame, selected_zone: str = "All Urban Zones"):
    """
    Donut chart of Property Classification breakdown across ALL properties.
    """
    title_text = "Property Classification Breakdown" if selected_zone == "All Urban Zones" else f"Classification — {selected_zone}"
    
    counts = df["Classification"].value_counts().reset_index()
    counts.columns = ["Classification", "Count"]
    
    total_outliers = counts[counts["Classification"] != "Normal"]["Count"].sum()
    
    fig = px.pie(
        counts,
        names="Classification",
        values="Count",
        color="Classification",
        color_discrete_map=COLOR_MAP,
        hole=0.62,
        title=f"<b>{title_text}</b>",
        template="plotly_dark"
    )
    
    fig.update_traces(
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Proportion: %{percent}<extra></extra>",
        marker=dict(line=dict(color="#151D28", width=2))
    )
    
    fig.add_annotation(
        text=f"<b>{total_outliers:,}</b><br><span style='font-size:11px;color:#9AA7B5;'>Outliers</span>",
        x=0.5, y=0.5,
        font=dict(size=20, color="#F5F7FA"),
        showarrow=False
    )
    
    fig.update_layout(**DARK_LAYOUT)
    fig.update_layout(
        height=400,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(color="#F5F7FA", size=11),
            bgcolor="rgba(21, 29, 40, 0.8)"
        )
    )
    return fig

def plot_outlier_visualization(df: pd.DataFrame, selected_zone: str = "All Urban Zones", currency_symbol: str = "₹", has_area: bool = True):
    """
    Scatter plot comparing Actual Price vs Expected Price. Retains 100% of outliers for perfect analytical visual map.
    """
    df_plot = _sample_for_plotting(df).copy()
    title_text = "Actual vs. Expected Price Outlier Map" if selected_zone == "All Urban Zones" else f"Actual vs. Expected Price Outlier Map — {selected_zone}"
    
    df_plot["hover_actual"] = df_plot["Actual Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_symbol))
    df_plot["hover_expected"] = df_plot["Expected Price"].apply(lambda x: format_currency_inr(x, currency_symbol=currency_symbol))
    df_plot["hover_diff_pct"] = df_plot["Price Difference (%)"].apply(lambda x: f"{x:+.1f}%")
    
    custom_cols = ["urban_zone", "property_type", "hover_actual", "hover_expected", "hover_diff_pct", "grubbs_result", "iqr_result"]
    
    fig = px.scatter(
        df_plot,
        x="Expected Price",
        y="Actual Price",
        color="Classification",
        color_discrete_map=COLOR_MAP,
        symbol="grubbs_outlier",
        hover_name="property_id",
        custom_data=custom_cols,
        title=f"<b>{title_text}</b>",
        template="plotly_dark"
    )
    
    max_p = max(df_plot["Actual Price"].max(), df_plot["Expected Price"].max())
    min_p = min(df_plot["Actual Price"].min(), df_plot["Expected Price"].min())
    
    fig.add_trace(
        gg.Scatter(
            x=[min_p, max_p],
            y=[min_p, max_p],
            mode="lines",
            name="1:1 Expected Benchmark",
            line=dict(color="#9AA7B5", dash="dash", width=1.5)
        )
    )
    
    bench_label = "Area-adjusted Expected Price" if has_area else "Zone Median Expected Price"
    hovertemplate = (
        "<b>Property ID:</b> %{hovertext}<br>" +
        "<b>Urban Zone:</b> %{customdata[0]}<br>" +
        "<b>Property Type:</b> %{customdata[1]}<br>" +
        "<b>Actual Price:</b> %{customdata[2]}<br>" +
        f"<b>Expected Price ({bench_label}):</b> %{{customdata[3]}}<br>" +
        "<b>Price Variance (%):</b> %{customdata[4]}<br>" +
        "<b>Grubbs Result:</b> %{customdata[5]}<br>" +
        "<b>IQR Result:</b> %{customdata[6]}<br>" +
        "<extra></extra>"
    )
    fig.update_traces(selector=dict(type='scatter', mode='markers'), hovertemplate=hovertemplate)
    
    x_title = f"Expected Price ({currency_symbol})" if has_area else f"Zone Median Benchmark ({currency_symbol})"
    return _apply_dark_style(fig, xaxis_title=x_title, yaxis_title=f"Actual Price ({currency_symbol})", height=450)

def plot_zone_comparison(df: pd.DataFrame, selected_zone: str = "All Urban Zones", currency_symbol: str = "₹", has_area: bool = True):
    """
    Grouped bar chart comparing Median and Mean metrics by Urban Zone across top zones.
    """
    title_text = "Price Metric Comparison by Urban Zone" if selected_zone == "All Urban Zones" else f"Rate Benchmark — {selected_zone}"
    
    if has_area and "price_per_sqft" in df.columns:
        metric_col = "price_per_sqft"
        y_label = f"Rate per Sq.Ft ({currency_symbol})"
        median_name = "Median Rate / Sq.Ft"
        mean_name = "Mean Rate / Sq.Ft"
    else:
        metric_col = "price"
        y_label = f"Transaction Price ({currency_symbol})"
        median_name = "Median Price"
        mean_name = "Mean Price"
        
    zone_stats = df.groupby("urban_zone", observed=True)[metric_col].agg(["mean", "median"]).reset_index()
    
    if len(zone_stats) > 25:
        zone_stats = zone_stats.sort_values(by="median", ascending=False).head(25)
        title_text += " (Top 25 Districts by Median)"
        
    fig = gg.Figure()
    fig.add_trace(gg.Bar(
        x=zone_stats["urban_zone"],
        y=zone_stats["median"],
        name=median_name,
        marker_color="#3B82F6"
    ))
    fig.add_trace(gg.Bar(
        x=zone_stats["urban_zone"],
        y=zone_stats["mean"],
        name=mean_name,
        marker_color="#F59E0B"
    ))
    
    fig.update_layout(
        barmode="group",
        title=dict(text=f"<b>{title_text}</b>", font=dict(color="#F5F7FA", size=15)),
        template="plotly_dark"
    )
    return _apply_dark_style(fig, xaxis_title="Urban Zone", yaxis_title=y_label, height=400)

def plot_price_by_property_type(df: pd.DataFrame, selected_zone: str = "All Urban Zones", currency_symbol: str = "₹"):
    """
    Box plot of transaction prices grouped by Property Type (Detached, Semi-Detached, Terraced, Flat, etc.).
    """
    if "property_type" not in df.columns or df["property_type"].nunique() <= 1:
        return None
        
    df_plot = _sample_for_plotting(df)
    title_text = "Price Distribution by Property Type" if selected_zone == "All Urban Zones" else f"Property Type Prices — {selected_zone}"
    
    fig = px.box(
        df_plot,
        x="property_type",
        y="price",
        color="property_type",
        points="outliers",
        title=f"<b>{title_text}</b>",
        labels={"price": f"Transaction Price ({currency_symbol})", "property_type": "Property Type"},
        hover_data=["property_id", "urban_zone"],
        template="plotly_dark"
    )
    
    return _apply_dark_style(fig, xaxis_title="Property Type", yaxis_title=f"Transaction Price ({currency_symbol})", height=420)

def plot_transaction_timeline(df: pd.DataFrame, selected_zone: str = "All Urban Zones", currency_symbol: str = "₹"):
    """
    Monthly transaction timeline showing volume and median price over time.
    """
    if "transaction_date" not in df.columns or df["transaction_date"].isna().all():
        return None
        
    df_time = df.dropna(subset=["transaction_date"]).copy()
    if df_time.empty:
        return None
        
    df_time["year_month"] = df_time["transaction_date"].dt.to_period("M").astype(str)
    
    monthly_stats = df_time.groupby("year_month").agg(
        count=("price", "count"),
        median_price=("price", "median"),
        mean_price=("price", "mean")
    ).reset_index()
    
    if len(monthly_stats) < 2:
        return None
        
    title_text = "Monthly Transaction Trends" if selected_zone == "All Urban Zones" else f"Transaction Trends — {selected_zone}"
    
    fig = gg.Figure()
    
    fig.add_trace(gg.Scatter(
        x=monthly_stats["year_month"],
        y=monthly_stats["median_price"],
        mode="lines+markers",
        name=f"Median Price ({currency_symbol})",
        line=dict(color="#3B82F6", width=2.5),
        marker=dict(size=6)
    ))
    
    fig.add_trace(gg.Bar(
        x=monthly_stats["year_month"],
        y=monthly_stats["count"],
        name="Transaction Volume",
        yaxis="y2",
        marker_color="rgba(148, 163, 184, 0.25)"
    ))
    
    fig.update_layout(
        title=dict(text=f"<b>{title_text}</b>", font=dict(color="#F5F7FA", size=15)),
        template="plotly_dark",
        yaxis2=dict(
            title="<b>Volume</b>",
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#9AA7B5", size=11)
        ),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(21, 29, 40, 0.8)")
    )
    
    return _apply_dark_style(fig, xaxis_title="Month", yaxis_title=f"Median Price ({currency_symbol})", height=420)
