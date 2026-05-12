# Gamma Geek — GEX Analytics Dashboard

A local Streamlit analytics dashboard for **Indian index options** that visualizes **Estimated Gamma Exposure (GEX)** for NIFTY, BANKNIFTY, FINNIFTY, and SENSEX.

## What this dashboard does
- Loads sample option-chain style data (or FYERS placeholder source).
- Calculates Black-Scholes gamma by strike.
- Converts gamma into **Estimated Gamma Exposure** proxies using OI and lot size.
- Shows KPIs, charts, alerts, and strategy interpretation zones.

## What GEX means
Gamma Exposure is an estimate of how option positioning may influence hedging behavior around spot and key strikes.

## Why this is estimated
Public option chain data does **not** reveal exact dealer inventory, client-dealer direction, or complete OTC positions. Therefore all values are labeled **Estimated Gamma Exposure** and should be treated as a proxy.

## Setup
1. `cd gamma-geek`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows)
4. `pip install -r requirements.txt`
5. `streamlit run app.py`

## FYERS API credentials (later)
1. Copy `.env.example` to `.env`
2. Add:
   - `FYERS_CLIENT_ID=...`
   - `FYERS_ACCESS_TOKEN=...`
3. The current `src/fyers_client.py` methods are placeholders where API calls can be added.

## Disclaimer
Educational and analytics only. Not financial advice. No order placement. No auto-trading.
