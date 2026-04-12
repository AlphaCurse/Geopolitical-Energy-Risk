import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Geopolitical Energy Risk", layout="wide")

# Sidebar for Scenario Testing
st.sidebar.header("🛡️ Hedge & Risk Controls")
vol_threshold = st.sidebar.slider("Volatility Alert Threshold", 0.10, 0.60, 0.40)

# Extract Live Commodity Data
tickers = ["BZ=F", "CL=F", "GC=F", "ITA"] # Brent, WTI, Gold, Defense
data = yf.download(tickers, period="6mo")['Close']
data['Spread'] = data['BZ=F'] - data['CL=F']

# Calculate Real-Time Volatility
returns = data['BZ=F'].pct_change()
current_vol = (returns.rolling(window=20).std() * np.sqrt(252)).iloc[-1]

# Dashboard Display
st.title("🛡️ Energy Risk Dashboard: Israel-Iran Conflict")

col1, col2 = st.columns(2)
with col1:
    st.metric("Brent-WTI Spread", f"${data['Spread'].iloc[-1]:.2f}", delta="Supply Risk")
with col2:
    if current_vol > vol_threshold:
        st.error(f"HIGH VOLATILITY: {current_vol:.2%}")
        st.warning("RECOMENDATION: Shift to Gold (GLD) & Defense (ITA)")
    else:
        st.success(f"STABLE VOLATILITY: {current_vol:.2%}")

st.plotly_chart(px.line(data, y="Spread", title="The 'War Premium' (Brent-WTI Spread)"))
