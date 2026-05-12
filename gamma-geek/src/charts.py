from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import THEME


def _base_layout(fig, title: str):
    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor=THEME["bg"],
        plot_bgcolor=THEME["bg"],
        font_color=THEME["text"],
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def strike_net_gex_chart(df: pd.DataFrame):
    colors = np.where(df["net_gex"] >= 0, THEME["positive"], THEME["negative"])
    fig = go.Figure(go.Bar(x=df["strike"], y=df["net_gex"], marker_color=colors, name="Net GEX"))
    return _base_layout(fig, "Estimated Net GEX by Strike")


def call_put_gex_chart(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_bar(x=df["strike"], y=df["call_gex"], name="Call GEX", marker_color=THEME["accent"])
    fig.add_bar(x=df["strike"], y=df["put_gex"], name="Put GEX", marker_color=THEME["negative"])
    fig.update_layout(barmode="group")
    return _base_layout(fig, "Estimated Call vs Put GEX")


def gamma_heatmap(df: pd.DataFrame):
    mat = np.vstack([df["call_gamma"].to_numpy(), -df["put_gamma"].to_numpy()])
    fig = px.imshow(mat, x=df["strike"], y=["Call Gamma", "-Put Gamma"], aspect="auto", color_continuous_scale="RdBu")
    return _base_layout(fig, "Gamma Intensity Heatmap")


def spot_overlay_chart(df: pd.DataFrame, spot: float):
    fig = go.Figure(go.Scatter(x=df["strike"], y=df["net_gex"], mode="lines+markers", name="Net GEX"))
    fig.add_vline(x=spot, line_width=2, line_dash="dash", line_color=THEME["accent"], annotation_text=f"Spot {spot:,.0f}")
    return _base_layout(fig, "Spot Overlay with Major Gamma Levels")


def expiry_placeholder(df: pd.DataFrame):
    agg = df.groupby("expiry", as_index=False)["net_gex"].sum()
    fig = px.bar(agg, x="expiry", y="net_gex", color="net_gex", color_continuous_scale="Tealrose")
    return _base_layout(fig, "Expiry-wise GEX Comparison (Placeholder)")
