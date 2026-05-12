from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

from config import EXPIRY_TO_DAYS, INDEX_CONFIG


def generate_sample_option_chain(index_name: str = "NIFTY", expiry_label: str = "Current Weekly", seed: int | None = None) -> pd.DataFrame:
    """Generate realistic-looking sample option chain for local analytics demos."""
    cfg = INDEX_CONFIG[index_name]
    rng = np.random.default_rng(seed)

    spot = float(cfg["spot"] + rng.normal(0, cfg["strike_step"] * 0.8))
    step = int(cfg["strike_step"])
    lot_size = int(cfg["lot_size"])

    if index_name == "NIFTY":
        strikes = np.arange(22000, 23001, 50)
    else:
        base_atm = round(spot / step) * step
        strikes = np.arange(base_atm - 10 * step, base_atm + 11 * step, step)

    atm_dist = np.abs(strikes - spot) / step
    base_oi = np.maximum(20000 * np.exp(-atm_dist / 6), 3000)

    call_oi = (base_oi * (0.9 + 0.25 * rng.random(len(strikes)))).astype(int)
    put_oi = (base_oi * (0.9 + 0.3 * rng.random(len(strikes)))).astype(int)

    intrinsic_call = np.maximum(spot - strikes, 0)
    intrinsic_put = np.maximum(strikes - spot, 0)
    time_value = np.maximum(120 - atm_dist * 4 + rng.normal(0, 3, len(strikes)), 12)

    call_ltp = np.maximum(intrinsic_call + time_value, 1.0)
    put_ltp = np.maximum(intrinsic_put + time_value, 1.0)

    call_iv = np.clip(0.12 + 0.02 * rng.random(len(strikes)) + atm_dist * 0.002, 0.10, 0.35)
    put_iv = np.clip(0.13 + 0.02 * rng.random(len(strikes)) + atm_dist * 0.002, 0.10, 0.38)

    now = pd.Timestamp(datetime.utcnow())
    expiry_days = EXPIRY_TO_DAYS[expiry_label]
    expiry = now.normalize() + pd.Timedelta(days=expiry_days)

    return pd.DataFrame(
        {
            "index": index_name,
            "spot": spot,
            "strike": strikes,
            "call_oi": call_oi,
            "put_oi": put_oi,
            "call_ltp": np.round(call_ltp, 2),
            "put_ltp": np.round(put_ltp, 2),
            "call_iv": np.round(call_iv, 4),
            "put_iv": np.round(put_iv, 4),
            "expiry": expiry.date().isoformat(),
            "lot_size": lot_size,
            "last_updated": now.isoformat(),
        }
    )


def save_default_sample_csv(path: str = "data/sample_option_chain.csv") -> None:
    df = generate_sample_option_chain("NIFTY", "Current Weekly", seed=42)
    df.to_csv(path, index=False)
