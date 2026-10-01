import plotly.express as px
import plotly.graph_objects as gg
import pandas as pd
from src.data_processing import format_currency_inr

# Phase 2 Design System Palette (Section 3)
COLOR_MAP = {
    "Normal": "#94A3B8",                # Neutral slate gray
    "Potentially Underpriced": "#22C55E", # Emerald green
    "Potentially Overpriced": "#EF4444",  # Red
    "Statistical Outlier": "#F59E0B"     # Amber yellow
}

# Phase 2 Dark Theme Plotly Options - Enhanced Visibility
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

def plot_price_distribution(df: pd.DataFrame, selected_zone: str = "All Urban Zones"):
    """
    Clean, high-visibility histogram of property prices with prominent Median (#22C55E) and Mean (#3B82F6) reference lines.
    """
    title_text = "Property Price Distribution" if selected_zone == "All Urban Zones" else f"Property Price Distribution — {selected_zone}"
    
    fig = px.histogram(
        df,
        x="price",
        color="urban_zone" if selected_zone == "All Urban Zones" else "Classification",
        color_discrete_map=COLOR_MAP if selected_zone != "All Urban Zones" else None,
        nbins=35,
        title=f"<b>{title_text}</b>",
        labels={"price": "Property Price (INR)", "urban_zone": "Urban Zone"},
        hover_data=["property_id", "area_sqft", "urban_zone"],
        template="plotly_dark",
        opacity=0.85
    )
    
    fig.update_traces(marker=dict(line=dict(color="#151D28", width=1)))
    
    mean_val = df["price"].mean()
    median_val = df["price"].median()
    
    # Prominent Mean and Median lines
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="#3B82F6",
        line_width=2.5,
        annotation_text=f"<b>Mean: {format_currency_inr(mean_val)}</b>",
        annotation_font_color="#3B82F6",
        annotation_position="top left"
    )
    fig.add_vline(
        x=median_val,
        line_dash="dot",
        line_color="#22C55E",
        line_width=2.5,
        annotation_text=f"<b>Median: {format_currency_inr(median_val)}</b>",
        annotation_font_color="#22C55E",
        annotation_position="top right"
    )
    
    return _apply_dark_style(fig, xaxis_title="Property Price (₹)", yaxis_title="Count", height=450)

def plot_box_plot_by_zone(df: pd.DataFrame, selected_zone: str = "All Urban Zones"):
    """
    Box plot showing price distribution and potential extreme observations per urban zone.
    """
    title_text = "Price Distribution & Outliers by Urban Zone" if selected_zone == "All Urban Zones" else f"Price Variance & Outliers — {selected_zone}"
    
    fig = px.box(
        df,
        x="urban_zone" if selected_zone == "All Urban Zones" else "property_type",
        y="price",
        color="urban_zone" if selected_zone == "All Urban Zones" else "property_type",
        points="outliers",
        title=f"<b>{title_text}</b>",
        labels={"price": "Property Price (INR)", "urban_zone": "Urban Zone", "property_type": "Property Type"},
        hover_data=["property_id", "area_sqft"],
        template="plotly_dark"
    )
    
    x_label = "Urban Zone" if selected_zone == "All Urban Zones" else "Property Type"
    return _apply_dark_style(fig, xaxis_title=x_label, yaxis_title="Property Price (₹)", height=450)

def plot_price_vs_area(df: pd.DataFrame, selected_zone: str = "All Urban Zones"):
    """
    High-visibility scatter plot of Price vs Area with crisp markers and contrast (Section 9 & 15).
    """
    df_plot = df.copy()
    title_text = "Property Price vs. Area (sq.ft)" if selected_zone == "All Urban Zones" else f"Property Price vs. Area (sq.ft) — {selected_zone}"
    
    df_plot["hover_actual_price"] = df_plot["Actual Price"].apply(lambda x: format_currency_inr(x))
    df_plot["hover_expected_price"] = df_plot["Expected Price"].apply(lambda x: format_currency_inr(x))
    df_plot["hover_price_diff"] = df_plot["Price Difference"].apply(lambda x: format_currency_inr(x, is_difference=True))
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
    
    return _apply_dark_style(fig, xaxis_title="Area (sq.ft)", yaxis_title="Property Price (₹)", height=450)

def plot_price_per_sqft_distribution(df: pd.DataFrame, selected_zone: str = "All Urban Zones"):
    """
    Violin / Box chart of Price per Square Foot by Urban Zone (Section 9).
    """
    title_text = "Price per Sq.Ft. by Urban Zone" if selected_zone == "All Urban Zones" else f"Price per Sq.Ft. — {selected_zone}"
    
    fig = px.violin(
        df,
        x="urban_zone" if selected_zone == "All Urban Zones" else "property_type",
        y="price_per_sqft",
        color="urban_zone" if selected_zone == "All Urban Zones" else "property_type",
        box=True,
        points="all",
        title=f"<b>{title_text}</b>",
        labels={"price_per_sqft": "Price / Sq.Ft (₹)", "urban_zone": "Urban Zone", "property_type": "Property Type"},
        hover_data=["property_id", "price"],
        template="plotly_dark"
    )
    
    x_label = "Urban Zone" if selected_zone == "All Urban Zones" else "Property Type"
    return _apply_dark_style(fig, xaxis_title=x_label, yaxis_title="Price per Sq.Ft (₹)", height=420)

def plot_classification_breakdown(df: pd.DataFrame, selected_zone: str = "All Urban Zones"):
    """
    Donut chart with fixed label overlap (Section 10 & 13).
    Labels outside tiny slices are turned off; center displays total count and clean side legend displays proportions.
    """
    title_text = "Property Classification" if selected_zone == "All Urban Zones" else f"Property Classification — {selected_zone}"
    
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
        text=f"<b>{total_outliers}</b><br><span style='font-size:11px;color:#9AA7B5;'>Outliers</span>",
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

def plot_outlier_visualization(df: pd.DataFrame, selected_zone: str = "All Urban Zones"):
    """
    Scatter plot comparing Actual Price vs Expected Price with dynamic title.
    """
    df_plot = df.copy()
    title_text = "Actual vs. Expected Price Outlier Map" if selected_zone == "All Urban Zones" else f"Actual vs. Expected Price Outlier Map — {selected_zone}"
    
    df_plot["hover_actual"] = df_plot["Actual Price"].apply(format_currency_inr)
    df_plot["hover_expected"] = df_plot["Expected Price"].apply(format_currency_inr)
    df_plot["hover_diff_pct"] = df_plot["Price Difference (%)"].apply(lambda x: f"{x:+.1f}%")
    
    fig = px.scatter(
        df_plot,
        x="Expected Price",
        y="Actual Price",
        color="Classification",
        color_discrete_map=COLOR_MAP,
        symbol="grubbs_outlier",
        hover_name="property_id",
        custom_data=["urban_zone", "area_sqft", "hover_actual", "hover_expected", "hover_diff_pct", "grubbs_result", "iqr_result"],
        title=f"<b>{title_text}</b>",
        template="plotly_dark"
    )
    
    max_p = max(df_plot["Actual Price"].max(), df_plot["Expected Price"].max())
    fig.add_trace(
        gg.Scatter(
            x=[0, max_p],
            y=[0, max_p],
            mode="lines",
            name="1:1 Expected Benchmark",
            line=dict(color="#9AA7B5", dash="dash", width=1.5)
        )
    )
    
    hovertemplate = (
        "<b>Property ID:</b> %{hovertext}<br>" +
        "<b>Urban Zone:</b> %{customdata[0]}<br>" +
        "<b>Area:</b> %{customdata[1]:,.0f} sq.ft<br>" +
        "<b>Actual Price:</b> %{customdata[2]}<br>" +
        "<b>Expected Price:</b> %{customdata[3]}<br>" +
        "<b>Price Difference (%):</b> %{customdata[4]}<br>" +
        "<b>Grubbs Result:</b> %{customdata[5]}<br>" +
        "<b>IQR Result:</b> %{customdata[6]}<br>" +
        "<extra></extra>"
    )
    fig.update_traces(selector=dict(type='scatter', mode='markers'), hovertemplate=hovertemplate)
    
    return _apply_dark_style(fig, xaxis_title="Expected Price (₹)", yaxis_title="Actual Price (₹)", height=450)

def plot_zone_comparison(df: pd.DataFrame, selected_zone: str = "All Urban Zones"):
    """
    Grouped bar chart comparing Median and Mean Price per sqft per urban zone.
    """
    title_text = "Price per Sq.Ft. by Urban Zone" if selected_zone == "All Urban Zones" else f"Rate Benchmark — {selected_zone}"
    
    zone_stats = df.groupby("urban_zone")["price_per_sqft"].agg(["mean", "median"]).reset_index()
    
    fig = gg.Figure()
    fig.add_trace(gg.Bar(
        x=zone_stats["urban_zone"],
        y=zone_stats["median"],
        name="Median Rate / Sq.Ft",
        marker_color="#3B82F6"
    ))
    fig.add_trace(gg.Bar(
        x=zone_stats["urban_zone"],
        y=zone_stats["mean"],
        name="Mean Rate / Sq.Ft",
        marker_color="#F59E0B"
    ))
    
    fig.update_layout(
        barmode="group",
        title=dict(text=f"<b>{title_text}</b>", font=dict(color="#F5F7FA", size=15)),
        template="plotly_dark"
    )
    return _apply_dark_style(fig, xaxis_title="Urban Zone", yaxis_title="Rate per Sq.Ft (₹)", height=400)
