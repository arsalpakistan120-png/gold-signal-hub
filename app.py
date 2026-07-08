import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, date, timedelta, timezone
import time, io, math

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="XAUUSD · Predictive Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  PREMIUM CSS  — Jannat-Level UI
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');

html, body, .stApp {
    background: #080B12 !important;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
}
</style>
""", unsafe_allow_html=True)


# /* — Metric boxes — */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #10141F, #151A28);
    border: 1px solid #1E2535;
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4);
}

/* ── Signal banner — HIGH PROBABILITY BUY ─────────────── */
.sig-hp-buy {
    background: linear-gradient(135deg, #071A0F 0%, #0D2B1A 60%, #071A0F 100%);
    border: 2px solid #00FF7F;
    border-radius: 16px;
    box-shadow: 0 0 30px rgba(0,255,127,0.25), 0 0 60px rgba(0,255,127,0.10);
    animation: pulse-green 2s ease-in-out infinite;
}
@keyframes pulse-green {
    0%,100% { box-shadow: 0 0 30px rgba(0,255,127,0.25), 0 0 60px rgba(0,255,127,0.08); }
    50%      { box-shadow: 0 0 45px rgba(0,255,127,0.45), 0 0 90px rgba(0,255,127,0.18); }
}

/* ── Signal banner — HIGH PROBABILITY SELL ────────────── */
.sig-hp-sell {
    background: linear-gradient(135deg, #1A0707 0%, #2B0D0D 60%, #1A0707 100%);
    border: 2px solid #FF3B3B;
    border-radius: 16px;
    box-shadow: 0 0 30px rgba(255,59,59,0.25), 0 0 60px rgba(255,59,59,0.10);
    animation: pulse-red 2s ease-in-out infinite;
}
@keyframes pulse-red {
    0%,100% { box-shadow: 0 0 30px rgba(255,59,59,0.25), 0 0 60px rgba(255,59,59,0.08); }
    50%      { box-shadow: 0 0 45px rgba(255,59,59,0.45), 0 0 90px rgba(255,59,59,0.18); }
}

/* ── Signal banner — MODERATE / WAIT ──────────────────── */
.sig-moderate {
    background: linear-gradient(135deg, #161A12 0%, #1E2318 60%, #161A12 100%);
    border: 2px solid #C8A820;
    border-radius: 16px;
    box-shadow: 0 0 20px rgba(200,168,32,0.15);
}
.sig-neutral {
    background: linear-gradient(135deg, #111318 0%, #18191F 100%);
    border: 2px solid #2E3244;
    border-radius: 16px;
}

/* ── Confirmation checklist ───────────────────────────── */
.confirm-row {
    display: flex; align-items: center; gap: 10px;
    padding: 7px 12px; border-radius: 7px;
    margin: 3px 0; font-size: 0.8rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
}
.confirm-yes { color: #00FF7F; font-size: 1rem; }
.confirm-no  { color: #3A3F50; font-size: 1rem; }
.confirm-txt-yes { color: #D0FFE8; }
.confirm-txt-no  { color: #3A3F50; }

/* ── Probability meter ────────────────────────────────── */
.prob-meter-bg {
    background: #1A1D27; border-radius: 30px; height: 12px;
    border: 1px solid #2A2D3A; overflow: hidden;
}
.prob-meter-fill {
    height: 12px; border-radius: 30px;
    transition: width 0.5s ease;
}

/* ── Risk / info boxes ────────────────────────────────── */
.card {
    background: linear-gradient(135deg, #10141F, #141828);
    border: 1px solid #1E2535;
    border-radius: 10px;
    padding: 11px 15px;
    margin: 3px 0;
    font-size: 0.85rem;
}
.card-label { color: #5A6080; font-size: 0.68rem; letter-spacing: 1.5px; text-transform: uppercase; }
.card-val   { color: #FFD700; font-weight: 800; font-size: 0.95rem; }
.card-sl    { color: #FF6B6B; font-weight: 700; }
.card-tp    { color: #4DFF9B; font-weight: 700; }
.card-lot   { color: #5BC8FF; font-weight: 700; }

/* ── S/R zone badge ───────────────────────────────────── */
.zone-support    { color: #00FF7F; background: rgba(0,255,127,0.08); border: 1px solid rgba(0,255,127,0.3); padding: 3px 8px; border-radius: 5px; font-size: 0.72rem; }
.zone-resistance { color: #FF5555; background: rgba(255,85,85,0.08); border: 1px solid rgba(255,85,85,0.3); padding: 3px 8px; border-radius: 5px; font-size: 0.72rem; }

/* ── Macro sentiment cards ────────────────────────────── */
.macro-card {
    background: #10141F; border: 1px solid #1E2535;
    border-radius: 9px; padding: 10px 12px; text-align: center;
}
.macro-label { color: #5A6080; font-size: 0.65rem; letter-spacing: 2px; }
.macro-val   { font-size: 1rem; font-weight: 800; margin: 3px 0; }
.macro-chg   { font-size: 0.72rem; }

/* ── Countdown box ────────────────────────────────────── */
.countdown-box {
    background: linear-gradient(135deg, #0D1020, #141828);
    border: 1px solid #2A2D4A;
    border-radius: 12px; padding: 14px 18px; text-align: center;
}
.countdown-label { color: #5A6080; font-size: 0.65rem; letter-spacing: 2px; }
.countdown-event { color: #FFD700; font-size: 0.8rem; font-weight: 700; margin: 4px 0; }
.countdown-timer { font-size: 1.6rem; font-weight: 900; letter-spacing: 4px; color: #FFFFFF; }
.countdown-impact-HIGH { color: #FF5555; font-size: 0.68rem; }
.countdown-impact-MED  { color: #FFD700; font-size: 0.68rem; }

/* ── Session badge ────────────────────────────────────── */
.session-active   { color: #00FF7F; background: rgba(0,255,127,0.08); border: 1px solid rgba(0,255,127,0.25); padding: 4px 10px; border-radius: 6px; font-size: 0.72rem; font-weight: 700; }
.session-inactive { color: #3A4060; background: rgba(58,64,96,0.2);   border: 1px solid #2A2D3A; padding: 4px 10px; border-radius: 6px; font-size: 0.72rem; }

/* ── Guard ────────────────────────────────────────────── */
.guard-active {
    background: rgba(255,50,50,0.08); border: 2px solid #FF3B3B;
    border-radius: 10px; padding: 14px; text-align: center;
    color: #FF5555; font-weight: 800; font-size: 0.9rem;
}
.guard-ok {
    background: rgba(0,200,100,0.05); border: 1px solid #1A4A2A;
    border-radius: 10px; padding: 10px; text-align: center;
    color: #4DFF9B; font-size: 0.8rem;
}

/* ── Section title ────────────────────────────────────── */
.sec-title {
    color: #3A4060; font-size: 0.62rem; letter-spacing: 3px;
    text-transform: uppercase; border-bottom: 1px solid #1A1D2A;
    padding-bottom: 5px; margin: 12px 0 8px 0;
}

/* ── MTF cards ────────────────────────────────────────── */
.mtf-card { background: #10141F; border: 1px solid #1E2535; border-radius: 8px; padding: 9px 7px; text-align: center; }
.mtf-label { font-size: 0.65rem; color: #5A6080; letter-spacing: 2px; }
.mtf-sig   { font-size: 0.95rem; font-weight: 900; letter-spacing: 2px; margin: 3px 0; }
.mtf-ema   { font-size: 0.62rem; color: #3A4060; }

/* ── Alignment badge ──────────────────────────────────── */
.align-badge {
    border-radius: 8px; padding: 10px 14px; font-size: 0.78rem;
    font-weight: 800; text-align: center; letter-spacing: 2px;
    height: 100%; display: flex; flex-direction: column; justify-content: center;
}
.align-strong   { background: rgba(0,255,127,0.07); border: 1px solid rgba(0,255,127,0.3); color: #00FF7F; }
.align-moderate { background: rgba(200,168,32,0.07); border: 1px solid rgba(200,168,32,0.3); color: #C8A820; }
.align-weak     { background: rgba(255,59,59,0.07); border: 1px solid rgba(255,59,59,0.3); color: #FF5555; }

/* ── Conf bar ─────────────────────────────────────────── */
.conf-bar-bg   { background: #1A1D27; border-radius: 4px; height: 6px; width: 100%; }
.conf-bar-fill { border-radius: 4px; height: 6px; }

/* ── Journal ──────────────────────────────────────────── */
.journal-card {
    background: #10141F; border: 1px solid #1E2535;
    border-radius: 9px; padding: 12px 16px; margin-bottom: 7px;
    font-size: 0.8rem;
}
.j-win  { border-left: 3px solid #00FF7F; }
.j-loss { border-left: 3px solid #FF5555; }
.j-be   { border-left: 3px solid #FFD700; }

section[data-testid="stSidebar"] { background: #060910 !important; border-right: 1px solid #1A1D2A; }
.stTabs [data-baseweb="tab-list"] { background: #080B12; }
.stTabs [data-baseweb="tab"]      { background: #10141F; color: #5A6080; border-radius: 6px 6px 0 0; }
.stTabs [aria-selected="true"]    { background: #141828 !important; color: #FFD700 !important; border-bottom: 2px solid #FFD700; }
div[data-testid="stExpander"]     { background: #10141F; border: 1px solid #1E2535; border-radius: 10px; }
#MainMenu, footer, header { visibility: hidden; }

/* ── ARSAL sticky navbar ─────────────────────────────────── */
.arsal-navbar {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 999999;
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    background: linear-gradient(90deg, #02040A 0%, #04070F 40%, #02040A 100%);
    border-bottom: 1px solid #1A2040;
    box-shadow: 0 2px 24px rgba(0,0,0,0.7);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}
.arsal-wordmark {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 1.55rem;
    font-weight: 900;
    letter-spacing: 10px;
    text-transform: uppercase;
    background: linear-gradient(135deg, #C8972A 0%, #FFD700 45%, #FFF0A0 60%, #FFD700 75%, #B8820A 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 8px rgba(255,215,0,0.35));
    user-select: none;
}
.arsal-tagline {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.52rem;
    letter-spacing: 3.5px;
    color: #2A3460;
    text-transform: uppercase;
    margin-top: 2px;
}
.arsal-divider {
    width: 1px; height: 28px;
    background: linear-gradient(180deg, transparent, #FFD70040, transparent);
    margin: 0 18px;
}
.arsal-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 2px;
    color: #3A4870;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
}
.arsal-live-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00FF7F;
    box-shadow: 0 0 6px #00FF7F;
    animation: blink 1.6s ease-in-out infinite;
}
@keyframes blink {
    0%,100% { opacity: 1; } 50% { opacity: 0.3; }
}
.arsal-ticker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 3px;
    color: #5A6FA0;
}

/* Push ALL Streamlit content below the fixed navbar */
.main .block-container {
    padding-top: 80px !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 68px !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "daily_pnl":             0.0,
        "account_balance":       10000.0,
        "initial_daily_balance": 10000.0,
        "daily_loss_hit":        False,
        "trade_log":             [],
        "current_date_tracked":  str(date.today()),
        "journal_entries":       [],
        "chart_tf":              "1d",
        "risk_pct":              1.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

today_str = str(date.today())
if st.session_state["current_date_tracked"] != today_str:
    st.session_state["daily_pnl"]            = 0.0
    st.session_state["initial_daily_balance"] = st.session_state["account_balance"]
    st.session_state["daily_loss_hit"]        = False
    st.session_state["current_date_tracked"]  = today_str

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════
TICKER          = "GC=F"
EMA_PERIOD      = 200
RSI_PERIOD      = 14
STOP_LOSS       = 1.5
TAKE_PROFIT     = 3.0
LOSS_LIMIT      = 0.05
POINT_VALUE_LOT = 100.0

TF_CONFIG = {
    "5m":  ("5m",  "60d",  200),
    "15m": ("15m", "60d",  180),
    "1h":  ("1h",  "730d", 200),
    "1d":  ("1d",  "2y",   120),
}
TF_LABELS   = list(TF_CONFIG.keys())
INTRADAY_TFS = ["5m", "15m", "1h"]

# Economic events 2026 (high-impact, UTC 13:30 unless noted)
ECON_EVENTS = [
    # NFP — first Friday each month 13:30 UTC
    ("2026-07-10", "NFP Non-Farm Payrolls",  "HIGH", "13:30"),
    ("2026-08-07", "NFP Non-Farm Payrolls",  "HIGH", "13:30"),
    ("2026-09-04", "NFP Non-Farm Payrolls",  "HIGH", "13:30"),
    ("2026-10-02", "NFP Non-Farm Payrolls",  "HIGH", "13:30"),
    ("2026-11-06", "NFP Non-Farm Payrolls",  "HIGH", "13:30"),
    ("2026-12-04", "NFP Non-Farm Payrolls",  "HIGH", "13:30"),
    # FOMC rate decisions 18:00 UTC
    ("2026-07-30", "FOMC Rate Decision",     "HIGH", "18:00"),
    ("2026-09-17", "FOMC Rate Decision",     "HIGH", "18:00"),
    ("2026-10-29", "FOMC Rate Decision",     "HIGH", "18:00"),
    ("2026-12-10", "FOMC Rate Decision",     "HIGH", "18:00"),
    # CPI — mid-month 12:30 UTC
    ("2026-07-14", "US CPI Inflation",       "HIGH", "12:30"),
    ("2026-08-12", "US CPI Inflation",       "HIGH", "12:30"),
    ("2026-09-11", "US CPI Inflation",       "HIGH", "12:30"),
    ("2026-10-14", "US CPI Inflation",       "HIGH", "12:30"),
    ("2026-11-12", "US CPI Inflation",       "HIGH", "12:30"),
    ("2026-12-09", "US CPI Inflation",       "HIGH", "12:30"),
    # PPI
    ("2026-07-15", "US PPI Producer Prices", "MED",  "12:30"),
    ("2026-08-13", "US PPI Producer Prices", "MED",  "12:30"),
    ("2026-09-15", "US PPI Producer Prices", "MED",  "12:30"),
    # Retail Sales
    ("2026-07-16", "US Retail Sales",        "MED",  "12:30"),
    ("2026-08-14", "US Retail Sales",        "MED",  "12:30"),
]

# Trading sessions (UTC open hour)
SESSIONS = {
    "Sydney":   (22, 7),    # 22:00–07:00 UTC
    "Tokyo":    (0,  9),
    "London":   (8,  17),   # Most gold movement
    "New York": (13, 22),   # Peak volatility
}

# ══════════════════════════════════════════════════════════════
#  INDICATOR CALCULATIONS
# ══════════════════════════════════════════════════════════════
def calc_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta    = series.diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rsi      = pd.Series(np.nan, index=series.index)
    both_zero = (avg_gain == 0) & (avg_loss == 0)
    only_gain = (avg_loss == 0) & (avg_gain > 0)
    only_loss = (avg_gain == 0) & (avg_loss > 0)
    normal    = ~both_zero & ~only_gain & ~only_loss
    rsi[both_zero] = 50.0
    rsi[only_gain] = 100.0
    rsi[only_loss] = 0.0
    rs = avg_gain[normal] / avg_loss[normal]
    rsi[normal] = 100 - (100 / (1 + rs))
    return rsi

# ══════════════════════════════════════════════════════════════
#  S/R ZONE DETECTION  (Institutional Order Flow)
# ══════════════════════════════════════════════════════════════
def identify_sr_zones(df: pd.DataFrame,
                      swing_window: int = 8,
                      cluster_pct: float = 0.0035,
                      price_range_pct: float = 0.06) -> list:
    """
    Detect institutional S/R zones from swing highs/lows.
    Returns list of zone dicts sorted by price.
    """
    if len(df) < swing_window * 2 + 5:
        return []

    closes  = df["close"].values
    highs   = df["high"].values
    lows    = df["low"].values
    vols    = df["volume"].values if "volume" in df.columns else np.ones(len(df))
    current = float(closes[-1])

    raw = []   # list of (price, type, touch_volume)

    for i in range(swing_window, len(df) - swing_window):
        # Swing high → resistance
        if highs[i] == max(highs[i - swing_window: i + swing_window + 1]):
            raw.append((float(highs[i]), "resistance", float(vols[i])))
        # Swing low → support
        if lows[i] == min(lows[i - swing_window: i + swing_window + 1]):
            raw.append((float(lows[i]), "support", float(vols[i])))

    if not raw:
        return []

    # Filter to relevant price range
    raw = [(p, t, v) for p, t, v in raw
           if abs(p - current) / current <= price_range_pct]
    if not raw:
        return []

    raw.sort(key=lambda x: x[0])

    # Cluster nearby levels
    zones = []
    used  = [False] * len(raw)
    for i in range(len(raw)):
        if used[i]:
            continue
        group = [raw[i]]
        used[i] = True
        for j in range(i + 1, len(raw)):
            if used[j]:
                continue
            if abs(raw[j][0] - raw[i][0]) / raw[i][0] < cluster_pct:
                group.append(raw[j])
                used[j] = True

        prices     = [g[0] for g in group]
        avg_price  = float(np.mean(prices))
        max_vol    = max(g[2] for g in group)
        strength   = len(group)
        sup_count  = sum(1 for g in group if g[1] == "support")
        zone_type  = "support" if sup_count >= len(group) / 2 else "resistance"
        spread     = avg_price * cluster_pct
        zones.append({
            "price":      avg_price,
            "zone_low":   avg_price - spread,
            "zone_high":  avg_price + spread,
            "type":       zone_type,
            "strength":   strength,
            "volume":     max_vol,
        })

    zones.sort(key=lambda z: z["price"])
    return zones

def nearest_zone(price: float, zones: list, tolerance_pct: float = 0.005):
    """Return nearest zone within tolerance, or None."""
    best, best_dist = None, float("inf")
    for z in zones:
        d = abs(z["price"] - price) / price
        if d < tolerance_pct and d < best_dist:
            best, best_dist = z, d
    return best

# ══════════════════════════════════════════════════════════════
#  RSI DIVERGENCE DETECTION
# ══════════════════════════════════════════════════════════════
def detect_rsi_divergence(df: pd.DataFrame, lookback: int = 50, swing_w: int = 3) -> str:
    """
    Detect RSI divergence using temporally aligned price/RSI pivots.
    We find swing-lows and swing-highs in **price**, then read RSI at those
    same bar indices — this ensures price and RSI pivots are time-matched.

    Bullish:  price makes lower-low but RSI at that same bar is higher-low  → BUY edge.
    Bearish:  price makes higher-high but RSI at that same bar is lower-high → SELL edge.
    Returns 'bullish' | 'bearish' | 'none'.
    """
    recent = df.tail(lookback).copy().dropna(subset=["rsi", "close"])
    if len(recent) < swing_w * 2 + 5:
        return "none"

    prices = recent["close"].values
    rsis   = recent["rsi"].values
    n      = len(prices)

    def pivot_lows(arr):
        """Return indices that are local minima within ±swing_w bars."""
        idx = []
        for i in range(swing_w, n - swing_w):
            window = arr[i - swing_w: i + swing_w + 1]
            if arr[i] <= window.min() + 1e-9:   # price is lowest in window
                idx.append(i)
        return idx

    def pivot_highs(arr):
        """Return indices that are local maxima within ±swing_w bars."""
        idx = []
        for i in range(swing_w, n - swing_w):
            window = arr[i - swing_w: i + swing_w + 1]
            if arr[i] >= window.max() - 1e-9:
                idx.append(i)
        return idx

    # ── Bullish divergence (find price lows, compare RSI *at those same bars*) ──
    p_low_idx = pivot_lows(prices)
    if len(p_low_idx) >= 2:
        i1, i2 = p_low_idx[-2], p_low_idx[-1]
        if prices[i2] < prices[i1] and rsis[i2] > rsis[i1]:
            return "bullish"

    # ── Bearish divergence (find price highs, compare RSI *at those same bars*) ──
    p_high_idx = pivot_highs(prices)
    if len(p_high_idx) >= 2:
        i1, i2 = p_high_idx[-2], p_high_idx[-1]
        if prices[i2] > prices[i1] and rsis[i2] < rsis[i1]:
            return "bearish"

    return "none"

# ══════════════════════════════════════════════════════════════
#  MACRO MARKET SENTIMENT  (DXY · VIX · TNX)
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def get_macro_sentiment() -> dict:
    """
    Fetch USD Index (DXY), VIX fear gauge, and 10Y Treasury yield.
    Gold correlations:
        DXY ↑  → Gold ↓ (strong negative)
        VIX ↑  → Gold ↑ (risk-off safe haven)
        TNX ↑  → Gold ↓ (opportunity cost)
    Returns composite sentiment for gold.
    """
    macro_tickers = {
        "DXY": "DX-Y.NYB",   # US Dollar Index
        "VIX": "^VIX",        # Fear gauge
        "TNX": "^TNX",        # 10-Year yield
    }
    results = {}
    for name, tkr in macro_tickers.items():
        try:
            df = yf.download(tkr, period="5d", interval="1d", progress=False)
            if df is None or df.empty:
                results[name] = {"value": None, "change": 0.0}
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0].lower() for c in df.columns]
            else:
                df.columns = [c.lower() for c in df.columns]
            if len(df) >= 2:
                v1 = float(df["close"].iloc[-2])
                v2 = float(df["close"].iloc[-1])
                chg = (v2 - v1) / v1 * 100 if v1 != 0 else 0.0
                results[name] = {"value": v2, "change": chg}
            else:
                results[name] = {"value": None, "change": 0.0}
        except Exception:
            results[name] = {"value": None, "change": 0.0}

    dxy_chg = results.get("DXY", {}).get("change", 0.0)
    vix_chg = results.get("VIX", {}).get("change", 0.0)
    tnx_chg = results.get("TNX", {}).get("change", 0.0)

    # Weighted composite (positive = bullish for gold)
    score = (-dxy_chg * 1.5) + (vix_chg * 0.6) + (-tnx_chg * 1.0)

    if score > 0.40:   sentiment = "BULLISH"
    elif score < -0.40: sentiment = "BEARISH"
    else:              sentiment = "NEUTRAL"

    return {
        "DXY": results["DXY"], "VIX": results["VIX"], "TNX": results["TNX"],
        "score": score, "sentiment": sentiment,
    }

# ══════════════════════════════════════════════════════════════
#  ECONOMIC CALENDAR
# ══════════════════════════════════════════════════════════════
def get_next_events(n: int = 3) -> list:
    """Return next N upcoming high-impact events with timezone-aware UTC datetimes."""
    now = datetime.now(timezone.utc)
    upcoming = []
    for date_str, name, impact, time_str in ECON_EVENTS:
        h, m     = map(int, time_str.split(":"))
        y, mo, d = map(int, date_str.split("-"))
        ev_dt    = datetime(y, mo, d, h, m, tzinfo=timezone.utc)   # explicit UTC
        if ev_dt > now:
            upcoming.append({"dt": ev_dt, "name": name, "impact": impact})
    upcoming.sort(key=lambda x: x["dt"])
    return upcoming[:n]

def countdown_html(ev: dict) -> str:
    """Return a self-updating JS countdown timer HTML block."""
    ts_ms = int(ev["dt"].timestamp() * 1000)
    impact_color = "#FF5555" if ev["impact"] == "HIGH" else "#FFD700"
    return f"""
<div class='countdown-box'>
    <div class='countdown-label'>NEXT HIGH-IMPACT EVENT</div>
    <div class='countdown-event'>{ev["name"]}</div>
    <div class='countdown-timer' id='cdtimer_{ts_ms}'>--:--:--</div>
    <div style='color:{impact_color};font-size:0.65rem;letter-spacing:2px;margin-top:3px;'>
        ● {ev["impact"]} IMPACT &nbsp;|&nbsp; {ev["dt"].strftime("%b %d %H:%M")} UTC
    </div>
</div>
<script>
(function() {{
    function tick() {{
        var diff = {ts_ms} - Date.now();
        if (diff <= 0) {{
            var el = document.getElementById('cdtimer_{ts_ms}');
            if (el) el.textContent = '⚡ LIVE NOW';
            return;
        }}
        var d = Math.floor(diff/86400000);
        var h = Math.floor((diff%86400000)/3600000);
        var m = Math.floor((diff%3600000)/60000);
        var s = Math.floor((diff%60000)/1000);
        var txt = (d>0 ? d+'d ' : '') +
                  String(h).padStart(2,'0') + ':' +
                  String(m).padStart(2,'0') + ':' +
                  String(s).padStart(2,'0');
        var el = document.getElementById('cdtimer_{ts_ms}');
        if (el) el.textContent = txt;
    }}
    tick();
    setInterval(tick, 1000);
}})();
</script>
"""

# ══════════════════════════════════════════════════════════════
#  TRADING SESSION INFO
# ══════════════════════════════════════════════════════════════
def get_session_info() -> dict:
    now_utc = datetime.utcnow()
    hour    = now_utc.hour
    active  = []
    for name, (open_h, close_h) in SESSIONS.items():
        if open_h < close_h:
            is_open = open_h <= hour < close_h
        else:                          # overnight (wraps midnight)
            is_open = hour >= open_h or hour < close_h
        if is_open:
            active.append(name)
    return {"active": active, "hour_utc": hour}

# ══════════════════════════════════════════════════════════════
#  DATA FETCH
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def fetch_data(ticker: str, interval: str = "1d", period: str = "2y") -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
    except Exception:
        return pd.DataFrame()
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0].lower() for c in df.columns]
    else:
        df.columns = [c.lower() for c in df.columns]
    if not {"open","high","low","close"}.issubset(set(df.columns)):
        return pd.DataFrame()
    df = df.dropna(subset=["close"])
    if len(df) < EMA_PERIOD + RSI_PERIOD + 5:
        return pd.DataFrame()
    df["ema200"] = calc_ema(df["close"], EMA_PERIOD)
    df["rsi"]    = calc_rsi(df["close"], RSI_PERIOD)
    df = df.dropna(subset=["ema200"])
    return df

# ══════════════════════════════════════════════════════════════
#  SMART MULTI-CONFIRMATION SIGNAL
# ══════════════════════════════════════════════════════════════
def smart_signal(df: pd.DataFrame, divergence: str,
                 at_zone, macro: dict) -> dict:
    """
    High-probability signal requiring multiple confirmations.
    Confirmations (each 0 or 1):
        1. EMA 200 trend direction
        2. Price at key S/R zone
        3. RSI divergence aligned
        4. Macro sentiment aligned
    Returns rich signal dict.
    """
    if df.empty:
        return {"signal": "WAIT", "score": 0, "max": 4, "pct": 0,
                "label": "NEUTRAL", "confirmations": {}, "price": 0.0,
                "ema200": 0.0, "rsi": 50.0, "sl": 0.0, "tp": 0.0}

    latest = df.iloc[-1]
    price  = float(latest["close"])
    ema200 = float(latest["ema200"])
    rsi    = float(latest["rsi"]) if not pd.isna(latest["rsi"]) else 50.0

    trend_bull = price > ema200
    trend_bear = price < ema200
    at_support = at_zone is not None and at_zone["type"] == "support"
    at_resist  = at_zone is not None and at_zone["type"] == "resistance"
    div_bull   = divergence == "bullish"
    div_bear   = divergence == "bearish"
    mac_bull   = macro["sentiment"] in ("BULLISH", "NEUTRAL")
    mac_bear   = macro["sentiment"] in ("BEARISH", "NEUTRAL")

    buy_score  = int(trend_bull) + int(at_support) + int(div_bull) + int(mac_bull)
    sell_score = int(trend_bear) + int(at_resist)  + int(div_bear) + int(mac_bear)

    if buy_score > sell_score and buy_score >= 2:
        signal = "BUY"
        score  = buy_score
        confirmations = {
            "EMA 200 Trend (Bullish)":       trend_bull,
            "Price at Support Zone":          at_support,
            "RSI Bullish Divergence":         div_bull,
            "Macro Sentiment Aligned":        mac_bull,
        }
    elif sell_score > buy_score and sell_score >= 2:
        signal = "SELL"
        score  = sell_score
        confirmations = {
            "EMA 200 Trend (Bearish)":        trend_bear,
            "Price at Resistance Zone":        at_resist,
            "RSI Bearish Divergence":          div_bear,
            "Macro Sentiment Aligned":         mac_bear,
        }
    else:
        signal = "WAIT"
        score  = max(buy_score, sell_score)
        confirmations = {
            "EMA 200 Trend Confirmed":        trend_bull or trend_bear,
            "Price at Key S/R Zone":          at_zone is not None,
            "RSI Divergence Detected":        divergence != "none",
            "Macro Sentiment Available":      macro["sentiment"] != "NEUTRAL",
        }

    # Label by conviction level
    if signal == "WAIT" or score < 2:
        label = "NEUTRAL"
        signal = "WAIT"
    elif score == 4:
        label = "HIGH PROBABILITY"
    elif score == 3:
        label = "MODERATE"
    else:
        label = "LOW CONFIDENCE"

    pct = int(score / 4 * 100)

    if signal == "BUY":
        sl, tp = price - STOP_LOSS, price + TAKE_PROFIT
    elif signal == "SELL":
        sl, tp = price + STOP_LOSS, price - TAKE_PROFIT
    else:
        sl, tp = price, price

    return {
        "signal": signal, "score": score, "max": 4, "pct": pct,
        "label": label, "confirmations": confirmations,
        "price": price, "ema200": ema200, "rsi": rsi,
        "sl": sl, "tp": tp,
    }

def generate_signal(df: pd.DataFrame):
    """Thin wrapper for legacy code paths."""
    if df.empty:
        return "WAIT", 0.0, 50.0, 0.0, 0.0
    l = df.iloc[-1]
    p = float(l["close"]); e = float(l["ema200"])
    r = float(l["rsi"]) if not pd.isna(l["rsi"]) else 50.0
    if p > e and r < 70:   sig = "BUY"
    elif p < e and r > 30: sig = "SELL"
    else:                  sig = "WAIT"
    return sig, p, r, e, 0.0

# ══════════════════════════════════════════════════════════════
#  LOT SIZE CALCULATOR
# ══════════════════════════════════════════════════════════════
def calc_lot_size(balance: float, risk_pct: float, sl_pts: float) -> float:
    if sl_pts <= 0:
        return 0.0
    return round(balance * (risk_pct / 100) / (sl_pts * POINT_VALUE_LOT), 2)

# ══════════════════════════════════════════════════════════════
#  CHART  (with S/R zones)
# ══════════════════════════════════════════════════════════════
def build_chart(df: pd.DataFrame, signal: str, tf_label: str,
                zones: list, divergence: str) -> go.Figure:
    _, _, bars = TF_CONFIG[tf_label]
    display    = df.tail(bars).copy()

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.68, 0.32], vertical_spacing=0.04,
        subplot_titles=("", "RSI (14) — Divergence Monitor"),
    )

    # ── Candlesticks ──────────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=display.index, open=display["open"], high=display["high"],
        low=display["low"], close=display["close"],
        name="Price",
        increasing_line_color="#00CC66", decreasing_line_color="#CC3333",
        increasing_fillcolor="#00CC66",  decreasing_fillcolor="#CC3333",
    ), row=1, col=1)

    # ── EMA 200 ───────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=display.index, y=display["ema200"],
        mode="lines", name="EMA 200",
        line=dict(color="#FFD700", width=2.5),
    ), row=1, col=1)

    # ── S/R Zones (drawn as transparent bands) ───────────────
    price_min = float(display["low"].min())
    price_max = float(display["high"].max())
    for z in zones:
        if z["zone_low"] > price_max or z["zone_high"] < price_min:
            continue
        color  = "rgba(0,200,100,0.07)"  if z["type"] == "support"    else "rgba(220,60,60,0.07)"
        border = "rgba(0,200,100,0.35)"  if z["type"] == "support"    else "rgba(220,60,60,0.35)"
        lbl    = f"S({z['strength']}✕)"  if z["type"] == "support"    else f"R({z['strength']}✕)"
        fig.add_hrect(y0=z["zone_low"], y1=z["zone_high"],
                      fillcolor=color, line_color=border, line_width=1,
                      opacity=1, row=1, col=1)
        fig.add_annotation(
            x=display.index[int(len(display) * 0.02)],
            y=z["price"], text=lbl,
            font=dict(size=9, color=border.replace("0.35","1")),
            showarrow=False, row=1, col=1,
        )

    # ── Signal marker ─────────────────────────────────────────
    lr = display.iloc[-1]; ld = display.index[-1]
    if signal == "BUY":
        my, ms, mc = float(lr["low"]) * 0.9993, "triangle-up",   "#00FF7F"
    elif signal == "SELL":
        my, ms, mc = float(lr["high"]) * 1.0007, "triangle-down", "#FF4444"
    else:
        my = None

    if my is not None:
        fig.add_trace(go.Scatter(
            x=[ld], y=[my], mode="markers", name=signal,
            marker=dict(symbol=ms, size=20, color=mc,
                        line=dict(color="white", width=2)),
        ), row=1, col=1)

    # ── RSI ───────────────────────────────────────────────────
    rsi_color = "#8B5CF6" if divergence == "none" else ("#00FF7F" if divergence == "bullish" else "#FF5555")
    fig.add_trace(go.Scatter(
        x=display.index, y=display["rsi"],
        mode="lines", name="RSI",
        line=dict(color=rsi_color, width=2),
        fill="tozeroy", fillcolor="rgba(139,92,246,0.04)",
    ), row=2, col=1)

    for lvl, col, dsh in [(70, "#CC3333","dash"),(50,"#303550","dot"),(30,"#00CC66","dash")]:
        fig.add_hline(y=lvl, line_color=col, line_dash=dsh, line_width=1, row=2, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(220,60,60,0.05)",  line_width=0, row=2, col=1)
    fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(0,200,100,0.05)", line_width=0, row=2, col=1)

    # Divergence annotation on RSI
    if divergence != "none":
        div_text  = "⬆ BULL DIV" if divergence == "bullish" else "⬇ BEAR DIV"
        div_color = "#00FF7F"     if divergence == "bullish" else "#FF5555"
        fig.add_annotation(
            x=display.index[-1], y=float(display["rsi"].iloc[-1]),
            text=div_text, font=dict(size=10, color=div_color),
            bgcolor="rgba(0,0,0,0.6)", bordercolor=div_color,
            showarrow=True, arrowcolor=div_color, row=2, col=1,
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#080B12", plot_bgcolor="#080B12",
        margin=dict(l=0, r=0, t=14, b=0),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.02, x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#5A6080")),
        font=dict(family="'JetBrains Mono', monospace", color="#8892A8"),
        height=480,
        xaxis2=dict(showgrid=True, gridcolor="#10141F"),
        yaxis=dict(showgrid=True, gridcolor="#10141F"),
        yaxis2=dict(showgrid=True, gridcolor="#10141F", range=[0, 100]),
    )
    return fig

# ══════════════════════════════════════════════════════════════
#  MTF ALIGNMENT
# ══════════════════════════════════════════════════════════════
def get_mtf_signals(ticker: str) -> dict:
    results = {}
    for label, (interval, period, _) in TF_CONFIG.items():
        df = fetch_data(ticker, interval, period)
        sig, price, rsi, ema200, _ = generate_signal(df)
        results[label] = (sig, price, rsi, ema200)
    return results

INTRADAY_TFS = ["5m", "15m", "1h"]

def mtf_alignment_score(mtf: dict, primary_signal: str):
    if primary_signal == "WAIT":
        return 0, "NEUTRAL"
    count = sum(1 for tf in INTRADAY_TFS if mtf.get(tf, ("WAIT",))[0] == primary_signal)
    return count, {3:"STRONG", 2:"MODERATE", 1:"WEAK"}.get(count, "CONFLICT")

# ══════════════════════════════════════════════════════════════
#  SAFETY GUARD
# ══════════════════════════════════════════════════════════════
def check_loss_limit() -> float:
    initial     = st.session_state["initial_daily_balance"]
    actual_loss = max(0.0, -st.session_state["daily_pnl"])
    pct         = actual_loss / initial if initial > 0 else 0.0
    if pct >= LOSS_LIMIT:
        st.session_state["daily_loss_hit"] = True
    return pct

# ══════════════════════════════════════════════════════════════
#  ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚡ TERMINAL SETTINGS")
    st.markdown("---")
    st.markdown("**Account**")
    new_bal = st.number_input("Balance (USD)", 100.0, 1_000_000.0,
                               st.session_state["account_balance"], 100.0, format="%.2f")
    if new_bal != st.session_state["account_balance"]:
        if not st.session_state["daily_loss_hit"]:
            st.session_state.update(account_balance=new_bal,
                                    initial_daily_balance=new_bal, daily_pnl=0.0)
        else:
            st.warning("⚠️ Guard active. Reset P&L first.")

    st.session_state["risk_pct"] = st.slider(
        "Risk per trade (%)", 0.25, 3.0,
        st.session_state["risk_pct"], 0.25, format="%.2f%%")

    st.markdown("---")
    st.markdown("**Signal Parameters**")
    st.markdown(f"""
| Parameter | Value |
|---|---|
| EMA Period | **{EMA_PERIOD}** |
| RSI Period | **{RSI_PERIOD}** |
| Stop-Loss  | **{STOP_LOSS} pts** |
| Take-Profit | **{TAKE_PROFIT} pts** |
| Daily Loss Limit | **{LOSS_LIMIT*100:.0f}%** |
| Min Confirmations | **2 / 4** |
""")

    st.markdown("---")
    st.markdown("**Confirmation Criteria**")
    st.markdown("""
- 📊 **EMA 200** Trend direction
- 🏛 **Inst. S/R Zone** proximity
- 📈 **RSI Divergence** detected
- 🌍 **Macro Sentiment** aligned
""")

    st.markdown("---")
    auto_refresh = st.toggle("Auto-refresh (60s)", False)
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear(); st.rerun()

    st.markdown("---")
    st.markdown("**Simulate P&L**")
    guard_active = st.session_state["daily_loss_hit"]
    if guard_active:
        st.markdown("<div style='font-size:0.7rem;color:#FF5555;text-align:center;"
                    "padding:5px;border:1px solid #FF5555;border-radius:5px;'>"
                    "🛡 Guard — trades blocked</div>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        if st.button("➕ +TP", use_container_width=True, disabled=guard_active):
            st.session_state["account_balance"] += TAKE_PROFIT
            st.session_state["daily_pnl"]       += TAKE_PROFIT
            st.session_state["trade_log"].append({"time": datetime.now().strftime("%H:%M:%S"), "result":"WIN",  "pnl":f"+${TAKE_PROFIT:.1f}"})
            check_loss_limit(); st.rerun()
    with cb:
        if st.button("➖ -SL", use_container_width=True, disabled=guard_active):
            st.session_state["account_balance"] -= STOP_LOSS
            st.session_state["daily_pnl"]       -= STOP_LOSS
            st.session_state["trade_log"].append({"time": datetime.now().strftime("%H:%M:%S"), "result":"LOSS", "pnl":f"-${STOP_LOSS:.1f}"})
            check_loss_limit(); st.rerun()
    if st.button("🔃 Reset Daily P&L", use_container_width=True):
        st.session_state.update(daily_pnl=0.0,
                                account_balance=st.session_state["initial_daily_balance"],
                                daily_loss_hit=False, trade_log=[])
        st.rerun()

# ══════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ══════════════════════════════════════════════════════════════

# ── ARSAL Fixed Navbar (rendered once, stays on top while scrolling) ──
st.markdown(f"""
<div class="arsal-navbar">

    <!-- LEFT: wordmark + tagline -->
    <div style="display:flex;flex-direction:column;justify-content:center;">
        <div class="arsal-wordmark">ARSAL</div>
        <div class="arsal-tagline">Institutional Trading Systems</div>
    </div>

    <!-- CENTER: decorative dividers + label -->
    <div style="display:flex;align-items:center;gap:0;">
        <div class="arsal-divider"></div>
        <span class="arsal-ticker">XAUUSD &nbsp;·&nbsp; PREDICTIVE ANALYZER</span>
        <div class="arsal-divider"></div>
    </div>

    <!-- RIGHT: live status -->
    <div class="arsal-badge">
        <div class="arsal-live-dot"></div>
        <span>MARKET LIVE</span>
        &nbsp;|&nbsp;
        <span style="color:#2A3460;">UTC {datetime.utcnow().strftime("%H:%M")}</span>
    </div>

</div>
""", unsafe_allow_html=True)

# ── Page sub-header (below the fixed navbar, inside scrollable content) ──
st.markdown("""
<div style="border-bottom:1px solid #0E1220;margin-bottom:16px;padding-bottom:10px;">
  <div style="font-size:0.6rem;color:#1E2535;letter-spacing:3px;text-transform:uppercase;">
      Institutional Order Flow &nbsp;·&nbsp; RSI Divergence &nbsp;·&nbsp;
      Macro Sentiment &nbsp;·&nbsp; Smart Trigger
  </div>
</div>
""", unsafe_allow_html=True)

# ── Fetch all data in parallel ────────────────────────────────
with st.spinner("Loading market intelligence..."):
    df_daily = fetch_data(TICKER, "1d", "2y")
    macro    = get_macro_sentiment()

if df_daily.empty:
    st.error("⚠️ Cannot reach market data. Please refresh."); st.stop()

# Compute all intelligence layers
zones      = identify_sr_zones(df_daily)
divergence = detect_rsi_divergence(df_daily)
sig_data   = smart_signal(df_daily, divergence, nearest_zone(
                float(df_daily["close"].iloc[-1]), zones), macro)
lot_size   = calc_lot_size(st.session_state["account_balance"],
                           st.session_state["risk_pct"], STOP_LOSS)
pct_loss   = check_loss_limit()
next_events = get_next_events(3)
session    = get_session_info()
price      = sig_data["price"]
rsi        = sig_data["rsi"]
ema200     = sig_data["ema200"]
signal     = sig_data["signal"]

# ── Top Metrics ───────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    pdelta = (f"{float(df_daily['close'].iloc[-1])-float(df_daily['close'].iloc[-2]):+.2f}"
              if len(df_daily) >= 2 else "—")
    st.metric("💰 GOLD (XAU/USD)", f"${price:,.2f}", pdelta)
with m2:
    st.metric("📊 EMA 200 (Daily)", f"${ema200:,.2f}", f"Δ {price-ema200:+.2f}")
with m3:
    rl = "Overbought" if rsi > 70 else ("Oversold" if rsi < 30 else "Neutral")
    st.metric(f"📈 RSI (14) · {rl}", f"{rsi:.1f}")
with m4:
    st.metric("📅 Daily P&L", f"${st.session_state['daily_pnl']:+.2f}",
              f"{pct_loss*100:.2f}% used", delta_color="inverse" if pct_loss > 0 else "normal")
with m5:
    st.metric("🏦 Balance", f"${st.session_state['account_balance']:,.2f}")

st.markdown("<div style='margin:14px 0'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  SMART SIGNAL BANNER  (full width)
# ══════════════════════════════════════════════════════════════
if st.session_state["daily_loss_hit"]:
    banner_class = "sig-neutral"
    banner_color = "#555"
    banner_title = "🛡  GUARD ACTIVE"
    banner_sub   = "Daily 5% loss limit reached. All signals suspended."
elif signal == "BUY" and sig_data["label"] == "HIGH PROBABILITY":
    banner_class = "sig-hp-buy"
    banner_color = "#00FF7F"
    banner_title = "▲  HIGH PROBABILITY BUY"
    banner_sub   = "All 4 confirmations aligned. Institutional flow supports entry."
elif signal == "SELL" and sig_data["label"] == "HIGH PROBABILITY":
    banner_class = "sig-hp-sell"
    banner_color = "#FF4444"
    banner_title = "▼  HIGH PROBABILITY SELL"
    banner_sub   = "All 4 confirmations aligned. Institutional flow supports entry."
elif signal == "BUY":
    banner_class = "sig-moderate"
    banner_color = "#C8A820"
    banner_title = f"▲  BUY — {sig_data['label']}"
    banner_sub   = f"{sig_data['score']}/4 confirmations. Wait for more confluence."
elif signal == "SELL":
    banner_class = "sig-moderate"
    banner_color = "#C8A820"
    banner_title = f"▼  SELL — {sig_data['label']}"
    banner_sub   = f"{sig_data['score']}/4 confirmations. Wait for more confluence."
else:
    banner_class = "sig-neutral"
    banner_color = "#3A4060"
    banner_title = "◆  NEUTRAL — WAIT"
    banner_sub   = "Insufficient confirmations. No edge detected."

pct = sig_data["pct"] if not st.session_state["daily_loss_hit"] else 0
meter_color = banner_color

conf_html = ""
for txt, confirmed in sig_data["confirmations"].items():
    icon    = "●" if confirmed else "○"
    cls_i   = "confirm-yes" if confirmed else "confirm-no"
    cls_t   = "confirm-txt-yes" if confirmed else "confirm-txt-no"
    conf_html += f"""<div class='confirm-row'>
        <span class='{cls_i}'>{icon}</span>
        <span class='{cls_t}'>{txt}</span>
    </div>"""

bc1, bc2, bc3 = st.columns([2, 1.8, 1.2])
with bc1:
    st.markdown(f"""
    <div class='{banner_class}' style='padding:20px 24px;'>
        <div style='font-size:0.65rem;color:{banner_color};letter-spacing:3px;opacity:0.7;'>
            SMART TRIGGER SIGNAL
        </div>
        <div style='font-size:1.9rem;font-weight:900;color:{banner_color};
             letter-spacing:5px;margin:6px 0 4px 0;'>{banner_title}</div>
        <div style='font-size:0.75rem;color:#5A6080;'>{banner_sub}</div>
        <div style='margin-top:12px;'>
            <div style='display:flex;justify-content:space-between;font-size:0.68rem;
                 color:#5A6080;margin-bottom:4px;'>
                <span>PROBABILITY SCORE</span>
                <span style='color:{meter_color};font-weight:800;'>{pct}% &nbsp;({sig_data["score"]}/{sig_data["max"]})</span>
            </div>
            <div class='prob-meter-bg'>
                <div class='prob-meter-fill'
                     style='width:{pct}%;background:linear-gradient(90deg,{meter_color}88,{meter_color});'>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if signal != "WAIT" and not st.session_state["daily_loss_hit"] and sig_data["label"] == "HIGH PROBABILITY":
        st.balloons()

with bc2:
    st.markdown(f"""
    <div style='background:#10141F;border:1px solid #1E2535;border-radius:12px;
         padding:16px;height:100%;'>
        <div class='sec-title'>CONFIRMATION CHECKLIST</div>
        {conf_html}
    </div>
    """, unsafe_allow_html=True)

with bc3:
    if next_events:
        st.markdown(countdown_html(next_events[0]), unsafe_allow_html=True)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        # Session info
        sess_html = ""
        for sname in ["London", "New York", "Tokyo", "Sydney"]:
            cls = "session-active" if sname in session["active"] else "session-inactive"
            sess_html += f"<span class='{cls}'>{sname}</span>&nbsp;"
        st.markdown(f"""
        <div style='background:#10141F;border:1px solid #1E2535;border-radius:10px;
             padding:10px;margin-top:4px;'>
            <div class='sec-title' style='margin-top:0;'>ACTIVE SESSIONS</div>
            {sess_html}
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MAIN LAYOUT:  LEFT PANEL  |  CHART
# ══════════════════════════════════════════════════════════════
left_col, right_col = st.columns([1, 2.9])

# ── LEFT PANEL ────────────────────────────────────────────────
with left_col:

    # Guard status
    if st.session_state["daily_loss_hit"]:
        st.markdown("<div class='guard-active'>🛡 SAFETY GUARD ACTIVE<br>"
                    "<span style='font-size:0.75rem;font-weight:normal;'>"
                    "5% daily loss limit reached. Signals DISABLED.</span></div>",
                    unsafe_allow_html=True)
    else:
        max_loss    = st.session_state["initial_daily_balance"] * LOSS_LIMIT
        actual_loss = max(0.0, -st.session_state["daily_pnl"])
        remaining   = max(0.0, max_loss - actual_loss)
        left_pct    = max(0.0, min(100.0, (1 - actual_loss/max_loss)*100) if max_loss else 100.0)
        st.markdown(f"<div class='guard-ok'>✅ GUARD OK — "
                    f"${remaining:.2f} buffer ({left_pct:.0f}% left)</div>",
                    unsafe_allow_html=True)

    # ── Risk Management + Lot Size ────────────────────────────
    st.markdown("<div class='sec-title'>RISK MANAGEMENT</div>", unsafe_allow_html=True)

    if not st.session_state["daily_loss_hit"] and signal != "WAIT":
        direction  = "LONG" if signal == "BUY" else "SHORT"
        risk_usd   = st.session_state["account_balance"] * st.session_state["risk_pct"] / 100
        at_zone    = nearest_zone(price, zones)
        zone_str   = (f"<span class='zone-{'support' if at_zone['type']=='support' else 'resistance'}'>"
                      f"{'S' if at_zone['type']=='support' else 'R'} ${at_zone['price']:,.1f} "
                      f"({at_zone['strength']}✕)</span>" if at_zone else "<span style='color:#3A4060'>None nearby</span>")
        st.markdown(f"""
        <div class='card'><div class='card-label'>DIRECTION</div>
            <div class='card-val'>{direction}</div></div>
        <div class='card'><div class='card-label'>ENTRY PRICE</div>
            <div class='card-val'>${price:,.2f}</div></div>
        <div class='card'><div class='card-label'>NEAREST ZONE</div>
            <div class='card-val'>{zone_str}</div></div>
        <div class='card'><div class='card-label'>STOP-LOSS ({STOP_LOSS} pts)</div>
            <div class='card-sl'>⬇ ${sig_data["sl"]:,.2f}</div></div>
        <div class='card'><div class='card-label'>TAKE-PROFIT ({TAKE_PROFIT} pts)</div>
            <div class='card-tp'>⬆ ${sig_data["tp"]:,.2f}</div></div>
        <div class='card'><div class='card-label'>RISK : REWARD</div>
            <div class='card-val'>1 : {TAKE_PROFIT/STOP_LOSS:.1f}</div></div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='card' style='text-align:center;color:#2A3050;'>— No active signal —</div>",
                    unsafe_allow_html=True)

    # ── Lot Size ─────────────────────────────────────────────
    st.markdown("<div class='sec-title'>LOT SIZE CALCULATOR</div>", unsafe_allow_html=True)
    r_usd     = st.session_state["account_balance"] * st.session_state["risk_pct"] / 100
    r_per_lot = STOP_LOSS * POINT_VALUE_LOT
    st.markdown(f"""
    <div class='card'><div class='card-label'>RISK % / TRADE</div>
        <div class='card-val'>{st.session_state["risk_pct"]:.2f}%</div></div>
    <div class='card'><div class='card-label'>MAX RISK (USD)</div>
        <div class='card-val'>${r_usd:,.2f}</div></div>
    <div class='card' style='border-color:#5BC8FF55;'>
        <div class='card-label'>✦ RECOMMENDED LOTS</div>
        <div class='card-lot' style='font-size:1.25rem;'>{lot_size:.2f} lots</div>
        <div style='color:#2A3050;font-size:0.62rem;margin-top:3px;'>
            ${r_usd:.0f} ÷ (${STOP_LOSS} × $100) = {lot_size:.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Macro Sentiment ───────────────────────────────────────
    st.markdown("<div class='sec-title'>MACRO MARKET SENTIMENT</div>", unsafe_allow_html=True)

    sent_color = {"BULLISH":"#00FF7F","BEARISH":"#FF5555","NEUTRAL":"#FFD700"}.get(macro["sentiment"],"#888")
    sent_icon  = {"BULLISH":"▲","BEARISH":"▼","NEUTRAL":"◆"}.get(macro["sentiment"],"◆")
    st.markdown(f"""
    <div style='text-align:center;padding:10px;background:#10141F;border:1px solid #1E2535;
         border-radius:10px;margin-bottom:8px;'>
        <div style='font-size:0.62rem;color:#3A4060;letter-spacing:2px;'>GOLD MACRO BIAS</div>
        <div style='font-size:1.3rem;font-weight:900;color:{sent_color};margin:4px 0;'>
            {sent_icon} {macro["sentiment"]}
        </div>
        <div style='font-size:0.65rem;color:#3A4060;'>score: {macro["score"]:+.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    mac1, mac2, mac3 = st.columns(3)
    for col, key, label, inv in [(mac1,"DXY","DXY",True),(mac2,"VIX","VIX",False),(mac3,"TNX","TNX",True)]:
        m    = macro[key]
        val  = f"{m['value']:.2f}" if m["value"] else "—"
        chg  = m["change"]
        # Gold impact: DXY↑ = bearish, VIX↑ = bullish, TNX↑ = bearish
        impact_color = ("#FF5555" if (inv and chg>0) or (not inv and chg<0)
                        else "#00CC66" if chg != 0 else "#5A6080")
        chg_str = f"{chg:+.2f}%" if m["value"] else "—"
        with col:
            st.markdown(f"""
            <div class='macro-card'>
                <div class='macro-label'>{label}</div>
                <div class='macro-val' style='color:#FFFFFF;'>{val}</div>
                <div class='macro-chg' style='color:{impact_color};'>{chg_str}</div>
            </div>""", unsafe_allow_html=True)

    # Divergence status
    st.markdown("<div class='sec-title'>RSI DIVERGENCE</div>", unsafe_allow_html=True)
    div_color = {"bullish":"#00FF7F","bearish":"#FF5555","none":"#3A4060"}.get(divergence,"#3A4060")
    div_icon  = {"bullish":"▲ BULLISH","bearish":"▼ BEARISH","none":"◆ NONE"}.get(divergence,"◆ NONE")
    st.markdown(f"""
    <div class='card' style='text-align:center;border-color:{div_color}33;'>
        <div style='color:{div_color};font-weight:800;font-size:0.95rem;'>{div_icon}</div>
        <div style='color:#3A4060;font-size:0.65rem;margin-top:3px;'>
            {"Confirmed divergence — watch for reversal" if divergence != "none" else "No divergence detected"}
        </div>
    </div>""", unsafe_allow_html=True)

    # S/R summary
    st.markdown("<div class='sec-title'>KEY INSTITUTIONAL ZONES</div>", unsafe_allow_html=True)
    near_zones = sorted(zones, key=lambda z: abs(z["price"] - price))[:5]
    if near_zones:
        for z in near_zones:
            dist    = (z["price"] - price)
            z_type  = z["type"]
            z_class = "zone-support" if z_type == "support" else "zone-resistance"
            strength_str = "★" * min(z["strength"], 5)
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;
                 padding:4px 0;border-bottom:1px solid #1A1D2A;'>
                <span class='{z_class}'>{"S" if z_type=="support" else "R"}</span>
                <span style='color:#8892A8;font-size:0.78rem;'>${z["price"]:,.2f}</span>
                <span style='color:#3A4060;font-size:0.7rem;'>{dist:+.1f}pt</span>
                <span style='color:#FFD700;font-size:0.65rem;'>{strength_str}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#2A3050;font-size:0.75rem;text-align:center;'>No zones detected in range</div>",
                    unsafe_allow_html=True)

    # Timestamp
    st.markdown(f"""<div style='font-size:0.62rem;color:#1E2535;margin-top:12px;text-align:center;'>
    LAST BAR: {df_daily.index[-1].strftime("%Y-%m-%d") if not df_daily.empty else "—"}<br>
    UTC: {datetime.utcnow().strftime("%H:%M:%S")}</div>""", unsafe_allow_html=True)

# ── RIGHT PANEL — CHART ───────────────────────────────────────
with right_col:

    # Timeframe selector
    tlabel_col, tbtn_col = st.columns([1, 3])
    with tlabel_col:
        st.markdown("<div style='font-size:0.65rem;color:#3A4060;letter-spacing:2px;"
                    "padding-top:8px;'>TIMEFRAME</div>", unsafe_allow_html=True)
    with tbtn_col:
        sel_tf = st.radio("tf", TF_LABELS,
                          index=TF_LABELS.index(st.session_state["chart_tf"]),
                          horizontal=True, label_visibility="collapsed")
        if sel_tf != st.session_state["chart_tf"]:
            st.session_state["chart_tf"] = sel_tf; st.rerun()

    tf_label = st.session_state["chart_tf"]
    iv, per, _ = TF_CONFIG[tf_label]
    df_chart   = df_daily if tf_label == "1d" else fetch_data(TICKER, iv, per)
    if df_chart.empty:
        st.warning(f"No {tf_label} data. Showing daily."); df_chart = df_daily; tf_label = "1d"

    chart_sig, *_ = generate_signal(df_chart)
    chart_divg    = detect_rsi_divergence(df_chart)
    chart_zones   = identify_sr_zones(df_chart) if tf_label != "1d" else zones

    st.markdown(f"<div class='sec-title'>XAUUSD · {tf_label.upper()} · EMA 200 · S/R ZONES</div>",
                unsafe_allow_html=True)
    st.plotly_chart(build_chart(df_chart, chart_sig, tf_label, chart_zones, chart_divg),
                    use_container_width=True, config={"displayModeBar": False})

    # ── MTF Alignment Panel ───────────────────────────────────
    st.markdown("<div class='sec-title'>MULTI-TIMEFRAME ALIGNMENT</div>", unsafe_allow_html=True)
    with st.spinner("Checking TF alignment..."):
        mtf = get_mtf_signals(TICKER)

    agree_count, strength = mtf_alignment_score(mtf, signal)
    align_css = {"STRONG":"align-strong","MODERATE":"align-moderate"}.get(strength,"align-weak")
    strength_icons = {"STRONG":"✦✦✦","MODERATE":"✦✦◇","WEAK":"✦◇◇","CONFLICT":"✗✗✗","NEUTRAL":"◇◇◇"}

    mc1,mc2,mc3,mc4,mbadge = st.columns([1,1,1,1,1.4])
    for tfn, col in [("5m",mc1),("15m",mc2),("1h",mc3),("1d",mc4)]:
        s, p, r, e = mtf[tfn]
        sc = {"BUY":"#00CC66","SELL":"#CC3333","WAIT":"#C8A820"}.get(s,"#888")
        si = {"BUY":"▲","SELL":"▼","WAIT":"◆"}.get(s,"◆")
        ab = "Above EMA" if p > e else "Below EMA"
        with col:
            st.markdown(f"""<div class='mtf-card'>
                <div class='mtf-label'>{tfn.upper()}</div>
                <div class='mtf-sig' style='color:{sc};'>{si} {s}</div>
                <div class='mtf-ema'>RSI {r:.0f} · {ab}</div>
            </div>""", unsafe_allow_html=True)

    with mbadge:
        st.markdown(f"""<div class='align-badge {align_css}'>
            {strength_icons.get(strength,"◇◇◇")}<br>{strength}<br>
            <span style='font-size:0.62rem;font-weight:400;'>{agree_count}/3 intraday<br>confirm daily</span>
        </div>""", unsafe_allow_html=True)

    # ── Upcoming Events Row ───────────────────────────────────
    if len(next_events) > 1:
        st.markdown("<div class='sec-title'>UPCOMING HIGH-IMPACT EVENTS</div>",
                    unsafe_allow_html=True)
        ev_cols = st.columns(min(len(next_events), 3))
        for i, ev in enumerate(next_events[:3]):
            days_away = (ev["dt"] - datetime.utcnow()).days
            ic = "#FF5555" if ev["impact"] == "HIGH" else "#FFD700"
            with ev_cols[i]:
                st.markdown(f"""
                <div class='card' style='text-align:center;'>
                    <div style='color:{ic};font-size:0.62rem;letter-spacing:1px;'>
                        ● {ev["impact"]} IMPACT
                    </div>
                    <div style='color:#D0D8F0;font-size:0.75rem;font-weight:700;margin:4px 0;'>
                        {ev["name"]}
                    </div>
                    <div style='color:#5A6080;font-size:0.68rem;'>
                        {ev["dt"].strftime("%b %d · %H:%M")} UTC
                    </div>
                    <div style='color:#FFD700;font-size:0.7rem;font-weight:700;'>
                        in {days_away}d {int(((ev["dt"]-datetime.utcnow()).seconds//3600))}h
                    </div>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  BOTTOM TABS
# ══════════════════════════════════════════════════════════════
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
tab_journal, tab_log = st.tabs(["📓  TRADE JOURNAL", "📋  TRADE LOG"])

# ── JOURNAL ───────────────────────────────────────────────────
with tab_journal:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    default_dir   = signal if signal != "WAIT" else "BUY"
    default_entry = f"{price:,.2f}"
    default_sl    = f"{sig_data['sl']:,.2f}" if signal != "WAIT" else ""
    default_tp    = f"{sig_data['tp']:,.2f}" if signal != "WAIT" else ""
    default_lots  = f"{lot_size:.2f}" if lot_size > 0 else ""

    with st.expander("➕ Log a New Trade", expanded=True):
        j1, j2, j3 = st.columns(3)
        with j1:
            j_date      = st.date_input("Date", date.today())
            j_direction = st.selectbox("Direction", ["BUY","SELL"], index=0 if default_dir=="BUY" else 1)
            j_tf        = st.selectbox("Timeframe", TF_LABELS, index=TF_LABELS.index("1d"),
                                       help="Pre-fills from Daily signal")
        with j2:
            j_entry    = st.text_input("Entry Price", default_entry)
            j_sl_price = st.text_input("Stop-Loss Price", default_sl)
            j_tp_price = st.text_input("Take-Profit Price", default_tp)
        with j3:
            j_lots   = st.text_input("Lot Size", default_lots)
            j_result = st.selectbox("Result", ["—","WIN","LOSS","BREAKEVEN"])
            j_pnl    = st.number_input("P&L (USD)", 0.0, step=0.50, format="%.2f")

        j_reason = st.text_area("Reason for Entry",
                                 placeholder="e.g. Price above EMA 200, RSI bullish divergence at support zone, macro BULLISH, 4/4 confirmations...",
                                 height=68)
        j_notes  = st.text_area("Post-Trade Notes",
                                  placeholder="e.g. TP hit cleanly. Should have waited for more confirmation...",
                                  height=68)

        if st.button("💾 Save Journal Entry", use_container_width=True):
            errors = []
            if not j_reason.strip():
                errors.append("Reason for entry is required.")

            def _pf(raw, name):
                try:
                    v = float(raw.replace(",","").strip())
                    if v <= 0: raise ValueError
                    return v, None
                except:
                    return None, f"{name} must be a positive number."

            ev, err = _pf(j_entry, "Entry Price");    err and errors.append(err)
            sv, err = _pf(j_sl_price, "Stop-Loss");   err and errors.append(err)
            tv, err = _pf(j_tp_price, "Take-Profit"); err and errors.append(err)
            lv, err = _pf(j_lots, "Lot Size");        err and errors.append(err)
            if j_result == "WIN"  and j_pnl <  0: errors.append("P&L must be positive for a WIN.")
            if j_result == "LOSS" and j_pnl >= 0: errors.append("P&L must be negative for a LOSS.")

            if errors:
                for e in errors: st.error(f"⚠️ {e}")
            else:
                st.session_state["journal_entries"].append({
                    "date": str(j_date), "time": datetime.now().strftime("%H:%M"),
                    "direction": j_direction, "tf": j_tf,
                    "entry": f"{ev:,.2f}", "sl": f"{sv:,.2f}", "tp": f"{tv:,.2f}",
                    "lots": f"{lv:.2f}", "result": j_result, "pnl": f"{j_pnl:+.2f}",
                    "reason": j_reason.strip(), "notes": j_notes.strip(),
                })
                st.success("✅ Trade saved!"); st.rerun()

    journal = st.session_state["journal_entries"]
    if not journal:
        st.markdown("<div style='color:#2A3050;text-align:center;padding:20px;"
                    "border:1px dashed #1E2535;border-radius:8px;'>"
                    "No journal entries yet.</div>", unsafe_allow_html=True)
    else:
        wins_j = sum(1 for e in journal if e["result"]=="WIN")
        losses_j = sum(1 for e in journal if e["result"]=="LOSS")
        total_j  = len(journal)
        wr_j     = wins_j/(wins_j+losses_j)*100 if (wins_j+losses_j) else 0
        total_pnl_j = sum(float(e["pnl"]) for e in journal)

        jm1,jm2,jm3,jm4,jm5 = st.columns(5)
        jm1.metric("Trades", total_j)
        jm2.metric("Wins", wins_j)
        jm3.metric("Losses", losses_j)
        jm4.metric("Win Rate", f"{wr_j:.0f}%")
        jm5.metric("Total P&L", f"${total_pnl_j:+.2f}")

        fc1, fc2 = st.columns([1, 3])
        with fc1: rf = st.selectbox("Filter", ["All","WIN","LOSS","BREAKEVEN","—"])
        with fc2: kw = st.text_input("Search", placeholder="keyword...")

        filtered = list(reversed(journal))
        if rf != "All":  filtered = [e for e in filtered if e["result"]==rf]
        if kw.strip():   filtered = [e for e in filtered if kw.lower() in e["reason"].lower() or kw.lower() in e["notes"].lower()]

        for entry in filtered:
            rc  = {"WIN":"j-win","LOSS":"j-loss","BREAKEVEN":"j-be"}.get(entry["result"],"")
            rco = {"WIN":"#00FF7F","LOSS":"#FF5555","BREAKEVEN":"#FFD700"}.get(entry["result"],"#888")
            dc  = "#00CC66" if entry["direction"]=="BUY" else "#CC3333"
            st.markdown(f"""
            <div class='journal-card {rc}'>
                <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
                    <span style='color:#3A4060;font-size:0.68rem;'>{entry["date"]} {entry["time"]} · {entry["tf"]}</span>
                    <span style='color:{rco};font-weight:700;font-size:0.78rem;'>{entry["result"]} {entry["pnl"]} USD</span>
                </div>
                <div style='display:flex;gap:14px;flex-wrap:wrap;margin-bottom:5px;'>
                    <span style='color:{dc};font-weight:700;'>{entry["direction"]}</span>
                    <span style='color:#3A4060;'>Entry: <b style='color:#FFD700;'>{entry["entry"]}</b></span>
                    <span style='color:#3A4060;'>SL: <b style='color:#FF6B6B;'>{entry["sl"]}</b></span>
                    <span style='color:#3A4060;'>TP: <b style='color:#4DFF9B;'>{entry["tp"]}</b></span>
                    <span style='color:#3A4060;'>Lots: <b style='color:#5BC8FF;'>{entry["lots"]}</b></span>
                </div>
                <div style='color:#8892A8;margin-bottom:3px;'><b style='color:#5A6080;'>Reason:</b> {entry["reason"]}</div>
                {f'<div style="color:#5A6080;font-size:0.75rem;"><b>Notes:</b> {entry["notes"]}</div>' if entry["notes"] else ""}
            </div>""", unsafe_allow_html=True)

        buf = io.StringIO()
        pd.DataFrame(journal).to_csv(buf, index=False)
        st.download_button("⬇️ Export CSV", buf.getvalue(),
                           f"xauusd_journal_{date.today()}.csv", "text/csv",
                           use_container_width=True)
        if st.button("🗑 Clear Journal", use_container_width=True):
            st.session_state["journal_entries"] = []; st.rerun()

# ── TRADE LOG ─────────────────────────────────────────────────
with tab_log:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    tlog = st.session_state["trade_log"]
    if not tlog:
        st.markdown("<div style='color:#2A3050;text-align:center;padding:20px;"
                    "border:1px dashed #1E2535;border-radius:8px;'>"
                    "No trades simulated yet. Use sidebar +TP / -SL buttons.</div>",
                    unsafe_allow_html=True)
    else:
        wins  = sum(1 for t in tlog if t["result"]=="WIN")
        total = len(tlog)
        lm1,lm2,lm3,lm4 = st.columns(4)
        lm1.metric("Trades", total)
        lm2.metric("Wins", wins)
        lm3.metric("Losses", total-wins)
        lm4.metric("Win Rate", f"{wins/total*100:.0f}%")
        st.dataframe(
            pd.DataFrame(reversed(tlog)).style.map(
                lambda v: "color: #00CC66" if v=="WIN" else ("color: #CC3333" if v=="LOSS" else ""),
                subset=["result"]),
            use_container_width=True, hide_index=True)

# ── AUTO REFRESH ─────────────────────────────────────────────
if auto_refresh:
    time.sleep(60); st.cache_data.clear(); st.rerun()
