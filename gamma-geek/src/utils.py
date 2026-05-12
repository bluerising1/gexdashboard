from __future__ import annotations

import pandas as pd


def filter_strikes(df: pd.DataFrame, spot: float, strike_range: str) -> pd.DataFrame:
    if strike_range == "All":
        return df
    step_count = int(strike_range.split("±")[-1])
    strike_step = (df["strike"].sort_values().diff().dropna().mode().iloc[0]) if len(df) > 1 else 50
    atm = min(df["strike"], key=lambda x: abs(x - spot))
    low = atm - step_count * strike_step
    high = atm + step_count * strike_step
    return df[(df["strike"] >= low) & (df["strike"] <= high)]


def format_units(value: float, units: str) -> str:
    if units == "Crores":
        return f"₹{value / 1e7:,.2f} Cr"
    if units == "Lakhs":
        return f"₹{value / 1e5:,.2f} L"
    return f"₹{value:,.0f}"
