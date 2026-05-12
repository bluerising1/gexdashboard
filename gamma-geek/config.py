from dataclasses import dataclass

INDEX_CONFIG = {
    "NIFTY": {"spot": 22500.0, "lot_size": 50, "strike_step": 50},
    "BANKNIFTY": {"spot": 48500.0, "lot_size": 15, "strike_step": 100},
    "FINNIFTY": {"spot": 23500.0, "lot_size": 40, "strike_step": 50},
    "SENSEX": {"spot": 74500.0, "lot_size": 10, "strike_step": 100},
}

EXPIRY_TO_DAYS = {
    "Current Weekly": 3,
    "Next Weekly": 10,
    "Monthly": 25,
}

CALCULATION_MODES = ["Basic OI-Based", "IV Adjusted", "Expiry Weighted"]
UNITS = ["Crores", "Lakhs", "Raw"]

@dataclass
class RiskConfig:
    risk_free_rate: float = 0.07
    regime_threshold_raw: float = 3e7


THEME = {
    "bg": "#0E1117",
    "card": "#1B1F2A",
    "text": "#E5ECF6",
    "positive": "#00C853",
    "negative": "#FF5252",
    "neutral": "#607D8B",
    "accent": "#29B6F6",
}
