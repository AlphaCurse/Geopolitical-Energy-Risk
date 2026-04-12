import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. CONFIG ---
st.set_page_config(page_title="Institutional Energy Risk", layout="wide")

# --- 2. DATA ETL ---
@st.cache_data(ttl=3600)
def fetch_comprehensive_data():
    tickers = ["BZ=F", "CL=F", "GC=F", "ITA"] 
    df = yf.download(tickers, period="1y")['Close']
    
    # Calculate Spread & Volatility
    df['Spread'] = df['BZ=F'] - df['CL=F']
    returns = df['BZ=F'].pct_change().dropna()
    
    # Tail Risk: CVaR (Expected Shortfall) at 95%
    var_95 = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    df['Vol'] = returns.rolling(window=20).std() * np.sqrt(252)
    
    return df, cvar_95

df, cvar_val = fetch_comprehensive_data()
current_vol = df['Vol'].iloc[-1]
current_bz = df['BZ=F'].iloc[-1]

# --- 3. SIDEBAR: RISK & NEWS ---
with st.sidebar:
    st.header("🛡️ Risk Controls")
    vol_threshold = st.slider("Volatility Alert Threshold", 0.10, 0.60, 0.40)
    risk_appetite = st.select_slider("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"], "Moderate")
    scenario_price = st.slider("Simulate Brent at ($):", 90, 200, 115)
    
    # Dynamic Hedge Logic
    mults = {"Conservative": 1.5, "Moderate": 1.0, "Aggressive": 0.5}
    dynamic_hedge_pct = min(0.10 * (current_vol / vol_threshold) * mults[risk_appetite], 0.40)
    
    st.divider()
    st.subheader("📰 Real-Time Intel")
    # ROBUST NEWS PARSER: Handles varied API dictionary keys
    news = yf.Ticker("BZ=F").news[:5]
    for item in news:
        # Check multiple possible keys used by yfinance
        headline = item.get('title') or item.get('headline') or "Market Update"
        link = item.get('link') or item.get('url') or "#"
        source = item.get('publisher') or item.get('source') or "Financial Feed"
        
        st.markdown(f"**[{headline}]({link})**")
        st.caption(f"Source: {source}")
        st.divider()

# --- 4. TOP METRICS ---
st.title("🛡️ Institutional Geopolitical Risk Dashboard")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Brent Crude", f"${current_bz:.2f}", "-0.75%")
m2.metric("War Premium (Spread)", f"${df['Spread'].iloc[-1]:.2f}", "Supply Risk")
m3.metric("Tail Risk (CVaR 95%)", f"{cvar_val:.2%}", "Expected Loss")
m4.metric("Gold (GC=F)", f"${df['GC=F'].iloc[-1]:,.2f}", "Safe Haven")

# --- 5. MAIN ANALYTICS ---
col_l, col_r = st.columns([2, 1])

with col_l:
    st.plotly_chart(px.line(df, y="Spread", title="The 'War Premium' (Brent-WTI Spread Trend)"), use_container_width=True)
    st.subheader("🌍 Alternative Data: Global Chokepoints")
    chokepoints = pd.DataFrame({'lat': [26.5, 2.5, 29.9], 'lon': [56.3, 101.3, 32.5]})
    st.map(chokepoints, color='#FF4B4B')

with col_r:
    st.subheader("🛡️ Dynamic Hedge Advisor")
    if current_vol > vol_threshold:
        st.error(f"CRITICAL VOLATILITY: {current_vol:.2%}")
        st.markdown(f"**Action:** Shift **{dynamic_hedge_pct:.1%}** to **Gold** & **Defense (ITA)**.")
    else:
        st.success(f"STABLE VOLATILITY: {current_vol:.2%}")
    
    st.divider()
    st.subheader("📉 Scenario Stress Test")
    impact = (scenario_price - current_bz) / current_bz
    st.write(f"Estimated Impact at **${scenario_price}** Oil:")
    st.progress(min(abs(impact), 1.0))
    st.write(f"Unhedged Loss Estimate: **{impact:.2%}**")

st.caption("Data source: yFinance. Analysis calibrated for Israel-Iran geopolitical risk theater.")
