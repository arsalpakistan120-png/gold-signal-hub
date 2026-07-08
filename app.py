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

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #10141F, #151A28);
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
