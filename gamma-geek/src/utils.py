from __future__ import annotations

from datetime import datetime, timedelta

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


def market_minutes_list() -> list[datetime]:
    start = datetime.strptime("09:00", "%H:%M")
    end = datetime.strptime("15:15", "%H:%M")
    vals: list[datetime] = []
    cur = start
    while cur <= end:
        vals.append(cur)
        cur += timedelta(minutes=5)
    return vals


def expiry_timeline_weight(expiry_label: str, minute_index: int, total_points: int) -> float:
    progress = minute_index / max(total_points - 1, 1)
    if expiry_label == "Current Weekly":
        return 1.0 + 0.20 * progress
    if expiry_label == "Next Weekly":
        return 1.0 + 0.10 * progress
    return 1.0 + 0.05 * progress
