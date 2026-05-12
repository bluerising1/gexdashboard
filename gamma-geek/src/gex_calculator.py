from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm


def black_scholes_gamma(spot: float, strike: np.ndarray, t: float, rate: float, iv: np.ndarray) -> np.ndarray:
    t = max(t, 1 / 365)
    iv = np.maximum(iv, 1e-4)
    d1 = (np.log(spot / strike) + (rate + 0.5 * iv**2) * t) / (iv * np.sqrt(t))
    gamma = norm.pdf(d1) / (spot * iv * np.sqrt(t))
    return gamma


def compute_gex(df: pd.DataFrame, spot: float, t_years: float, rate: float, mode: str) -> pd.DataFrame:
    out = df.copy()
    out["call_gamma"] = black_scholes_gamma(spot, out["strike"].to_numpy(), t_years, rate, out["call_iv"].to_numpy())
    out["put_gamma"] = black_scholes_gamma(spot, out["strike"].to_numpy(), t_years, rate, out["put_iv"].to_numpy())

    mode_factor = 1.0
    if mode == "IV Adjusted":
        mode_factor = (out["call_iv"] + out["put_iv"]) / 2 / 0.15
    elif mode == "Expiry Weighted":
        mode_factor = 1 / np.sqrt(max(t_years, 1 / 365))

    out["call_gex"] = out["call_oi"] * out["lot_size"] * out["call_gamma"] * (spot**2) * 0.01 * mode_factor
    out["put_gex"] = out["put_oi"] * out["lot_size"] * out["put_gamma"] * (spot**2) * 0.01 * mode_factor
    out["net_gex"] = out["call_gex"] - out["put_gex"]
    out = out.sort_values("strike").reset_index(drop=True)
    out["cum_net_gex"] = out["net_gex"].cumsum()
    return out


def estimate_gamma_flip(df: pd.DataFrame) -> float:
    signs = np.sign(df["cum_net_gex"])  # cumulative sign
    sign_changes = np.where(np.diff(signs) != 0)[0]
    if len(sign_changes) > 0:
        idx = sign_changes[0] + 1
        return float(df.iloc[idx]["strike"])
    closest_idx = (df["cum_net_gex"].abs()).idxmin()
    return float(df.iloc[closest_idx]["strike"])


def market_regime(total_gex: float, threshold: float) -> str:
    if total_gex > threshold:
        return "Positive Gamma"
    if total_gex < -threshold:
        return "Negative Gamma"
    return "Neutral"
