#!/usr/bin/env python3
"""
Trading Dashboard - Streamlit app for viewing trading metrics.
Connects to the FastAPI trading system API.
"""
import os
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Config
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Pulse V1 Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Sidebar ────────────────────────────────────────────────────────

st.sidebar.title("⚙️ Controls")
if st.sidebar.button("🔄 Refresh"):
    st.rerun()

auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
if auto_refresh:
    st.sidebar.caption("Refreshing every 30 seconds...")
    import time
    time.sleep(30)
    st.rerun()

# ─── API Helpers ────────────────────────────────────────────────────

def api_get(endpoint: str):
    """GET request to API."""
    try:
        resp = requests.get(f"{API_URL}{endpoint}", timeout=5)
        return resp.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def api_post(endpoint: str):
    """POST request to API."""
    try:
        resp = requests.post(f"{API_URL}{endpoint}", timeout=5)
        return resp.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# ─── Header ─────────────────────────────────────────────────────────

st.title("📈 Pulse V1 Trading Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ─── Status Row ─────────────────────────────────────────────────────

status = api_get("/api/status")
if status:
    cols = st.columns(6)
    cols[0].metric("Status", status.get("status", "unknown").upper())
    cols[1].metric("Mode", status.get("mode", "unknown").upper())
    cols[2].metric("Portfolio", f"${status.get('portfolio_value', 0):,.2f}")
    cols[3].metric("Buying Power", f"${status.get('buying_power', 0):,.2f}")
    cols[4].metric("Daily PnL", f"${status.get('daily_pnl', 0):+.2f}")
    cols[5].metric("Active Positions", status.get("active_positions", 0))
    
    # Control buttons
    ctrl_cols = st.columns(4)
    if ctrl_cols[0].button("▶️ Start Trading"):
        api_post("/api/start")
        st.success("Trading started!")
    if ctrl_cols[1].button("⏹️ Stop Trading"):
        api_post("/api/stop")
        st.success("Trading stopped!")
    if ctrl_cols[2].button("📕 Close All"):
        api_post("/api/close-all")
        st.success("All positions closed!")
    if ctrl_cols[3].button("❌ Cancel Orders"):
        api_post("/api/cancel-all")
        st.success("All orders cancelled!")

st.divider()

# ─── Two Column Layout ─────────────────────────────────────────────

left_col, right_col = st.columns([2, 1])

with left_col:
    # ─── Positions ──────────────────────────────────────────────────
    st.subheader("📊 Active Positions")
    positions = api_get("/api/positions")
    if positions:
        df = pd.DataFrame(positions)
        df["pnl"] = df["pnl"].apply(lambda x: f"${x:+.2f}")
        df["pnl_pct"] = df["pnl_pct"].apply(lambda x: f"{x:+.2%}")
        df["entry"] = df["entry"].apply(lambda x: f"${x:.2f}")
        df["current_price"] = df["current_price"].apply(lambda x: f"${x:.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No active positions")

    # ─── Trade History ─────────────────────────────────────────────
    st.subheader("📜 Trade History")
    trades = api_get("/api/trades")
    if trades:
        df = pd.DataFrame(trades)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No trades yet")

    # ─── Daily Stats ───────────────────────────────────────────────
    st.subheader("📅 Daily Statistics")
    daily = api_get("/api/daily")
    if daily:
        df = pd.DataFrame(daily)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No daily stats yet")

with right_col:
    # ─── Account ───────────────────────────────────────────────────
    st.subheader("💰 Account")
    account = api_get("/api/account")
    if account:
        st.metric("Equity", f"${account.get('equity', 0):,.2f}")
        st.metric("Cash", f"${account.get('cash', 0):,.2f}")
        st.metric("Buying Power", f"${account.get('buying_power', 0):,.2f}")
        st.metric("Day Trades", account.get("daytrade_count", 0))
        st.write(f"**PDT:** {'⚠️ Yes' if account.get('pattern_day_trader') else '✅ No'}")
        st.write(f"**Blocked:** {'🚫 Yes' if account.get('trading_blocked') else '✅ No'}")

    # ─── Orders ────────────────────────────────────────────────────
    st.subheader("📋 Open Orders")
    orders = api_get("/api/orders?status=open")
    if orders:
        for o in orders:
            st.write(f"**{o['symbol']}** {o['side']} x{o['qty']} @ {o.get('limit_price', 'market')}")
    else:
        st.info("No open orders")

    # ─── Market Clock ──────────────────────────────────────────────
    st.subheader("🕐 Market Clock")
    clock = api_get("/api/clock")
    if clock:
        st.write(f"**Open:** {'🟢 Yes' if clock.get('is_open') else '🔴 No'}")
        st.write(f"Next Open: {clock.get('next_open', 'N/A')}")
        st.write(f"Next Close: {clock.get('next_close', 'N/A')}")

    # ─── Scan Results ──────────────────────────────────────────────
    st.subheader("🔍 Pre-Market Scan")
    scan = api_get("/api/scan")
    if scan:
        for s in scan[:5]:
            emoji = "🟢" if s["direction"] == "long" else "🔴"
            st.write(f"{emoji} **{s['symbol']}** | Gap: {s['gap_pct']:+.2%} | Vol: {s['pm_volume']:,}")
    else:
        st.info("No setups found")

st.divider()

# ─── Footer ─────────────────────────────────────────────────────────

st.caption("Pulse V1 Trading System | Built with FastAPI + Streamlit")
