from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from config import CALCULATION_MODES, EXPIRY_TO_DAYS, INDEX_CONFIG, RiskConfig, THEME, UNITS
from src.charts import call_put_gex_chart, expiry_placeholder, gamma_heatmap, spot_overlay_chart, strike_net_gex_chart
from src.fyers_client import FyersClient
from src.gex_calculator import compute_gex, estimate_gamma_flip, market_regime
from src.sample_data import generate_sample_option_chain
from src.utils import filter_strikes, format_units

st.set_page_config(page_title="Gamma Geek — GEX Analytics Dashboard", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{background-color: {THEME['bg']}; color: {THEME['text']};}}
    .block-container {{padding-top: 1.5rem;}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Gamma Geek — Estimated Gamma Exposure Dashboard")
st.caption("For Indian Index Options | Analytics Only | No Auto Trading")
st.warning("All values shown are **Estimated Gamma Exposure** based on public option chain/OI proxies.")

with st.sidebar:
    st.header("Controls")
    index_name = st.selectbox("Index", ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"])
    expiry_label = st.selectbox("Expiry", ["Current Weekly", "Next Weekly", "Monthly"])
    strike_range = st.selectbox("Strike Range", ["ATM ±5", "ATM ±10", "ATM ±20", "All"])
    refresh = st.selectbox("Refresh Mode", ["Manual", "5 sec", "15 sec", "60 sec"])
    data_source = st.selectbox("Data Source", ["Sample Data", "FYERS Placeholder"])
    calc_mode = st.selectbox("Calculation Mode", CALCULATION_MODES)
    units = st.selectbox("Units", UNITS)
    st.caption("Theme: Dark premium fintech")

    st.subheader("Custom Strategy Builder")
    flip_buffer = st.number_input("Gamma flip buffer (pts)", min_value=10, max_value=1000, value=100, step=10)
    wall_proximity = st.number_input("Gamma wall proximity (pts)", min_value=10, max_value=1000, value=150, step=10)
    min_gex_threshold = st.number_input("Minimum GEX threshold", min_value=100000, value=5000000, step=100000)

cfg = INDEX_CONFIG[index_name]
risk = RiskConfig()

if refresh != "Manual":
    st.caption(f"Auto-refresh placeholder selected: {refresh} (use Streamlit autorefresh component for production).")

fyers = FyersClient()
if data_source == "FYERS Placeholder" and not fyers.has_credentials:
    st.warning("FYERS credentials missing. Falling back to sample data.")

raw_df = generate_sample_option_chain(index_name=index_name, expiry_label=expiry_label)
spot = float(raw_df["spot"].iloc[0])

df = filter_strikes(raw_df, spot, strike_range)
t_years = EXPIRY_TO_DAYS[expiry_label] / 365

gex_df = compute_gex(df, spot=spot, t_years=t_years, rate=risk.risk_free_rate, mode=calc_mode)

total_gex = float(gex_df["net_gex"].sum())
abs_exposure = float(gex_df["net_gex"].abs().sum())
flip = estimate_gamma_flip(gex_df)
max_pos = float(gex_df.loc[gex_df["net_gex"].idxmax(), "strike"])
max_neg = float(gex_df.loc[gex_df["net_gex"].idxmin(), "strike"])
regime = market_regime(total_gex, risk.regime_threshold_raw)

cols = st.columns(7)
cols[0].metric("Spot Price", f"{spot:,.2f}")
cols[1].metric("Net GEX", format_units(total_gex, units))
cols[2].metric("Total Absolute Exposure", format_units(abs_exposure, units))
cols[3].metric("Gamma Flip Point", f"{flip:,.0f}")
cols[4].metric("Max Positive GEX Strike", f"{max_pos:,.0f}")
cols[5].metric("Max Negative GEX Strike", f"{max_neg:,.0f}")
cols[6].metric("Market Regime", regime)

c1, c2 = st.columns(2)
c1.plotly_chart(strike_net_gex_chart(gex_df), use_container_width=True)
c2.plotly_chart(call_put_gex_chart(gex_df), use_container_width=True)

c3, c4 = st.columns(2)
c3.plotly_chart(gamma_heatmap(gex_df), use_container_width=True)
c4.plotly_chart(spot_overlay_chart(gex_df, spot), use_container_width=True)

st.plotly_chart(expiry_placeholder(gex_df), use_container_width=True)

st.subheader("Estimated Gamma Exposure Option Chain")
show_cols = [
    "strike", "call_oi", "put_oi", "call_ltp", "put_ltp", "call_iv", "put_iv",
    "call_gamma", "put_gamma", "call_gex", "put_gex", "net_gex"
]
st.dataframe(gex_df[show_cols].round(4), use_container_width=True)

st.subheader("Alerts")
if abs(spot - max_pos) <= wall_proximity:
    st.success("Spot is near a major positive gamma wall (Estimated).")
if abs(spot - max_neg) <= wall_proximity:
    st.error("Spot is near a major negative gamma zone (Estimated).")
if spot > flip + flip_buffer:
    st.info("Spot is above gamma flip buffer: possible momentum expansion zone.")
elif spot < flip - flip_buffer:
    st.info("Spot is below gamma flip buffer: possible momentum expansion zone.")
else:
    st.info("Spot is near gamma flip: potential mean reversion / chop zone.")

st.write(f"Market regime is **{regime}** based on Estimated Gamma Exposure.")
last_updated = pd.to_datetime(raw_df['last_updated'].iloc[0])
if (datetime.utcnow() - last_updated.to_pydatetime()).seconds > 120:
    st.warning("Data stale warning: feed appears older than 120 seconds (placeholder rule).")

st.subheader("Custom Strategy Interpretation")
if abs(total_gex) < min_gex_threshold:
    st.write("Neutral / no trade zone: Estimated gamma support is weak.")
elif regime == "Positive Gamma" and abs(spot - flip) <= flip_buffer:
    st.write("Mean reversion zone: positive gamma with spot near flip often dampens volatility.")
elif regime == "Negative Gamma" or abs(spot - flip) > flip_buffer:
    st.write("Momentum expansion zone: negative gamma or far-from-flip conditions can amplify moves.")
else:
    st.write("Neutral conditions: wait for stronger Estimated Gamma Exposure alignment.")

st.caption("No order placement. No auto-trading. Analytics-only dashboard.")
