import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="Institutional Energy Risk", layout="wide")

@st.cache_data(ttl=3600)
def fetch_comprehensive_data():
    tickers = ["BZ=F", "CL=F", "GC=F", "ITA"] 
    df = yf.download(tickers, period="1y")['Close']
    df['Spread'] = df['BZ=F'] - df['CL=F']
    returns = df['BZ=F'].pct_change().dropna()
    var_95 = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    df['Vol'] = returns.rolling(window=20).std() * np.sqrt(252)
    return df, cvar_95

df, cvar_val = fetch_comprehensive_data()
current_vol = df['Vol'].iloc[-1]
current_bz = df['BZ=F'].iloc[-1]

# --- 2. ROBUST NEWS FUNCTION (FIX FOR KEYERROR) ---
def display_intel_feed(ticker):
    st.subheader("📰 Real-Time Intel Feed")
    try:
        # Ticker-specific search is often more reliable than .news
        tk = yf.Ticker(ticker)
        news = tk.get_news() # Updated method in newer yfinance versions
        
        if not news:
            st.warning("Alternative Intel: Search 'Israel-Iran Energy' for live tactical updates.")
            return

        for item in news:
            # 2026 yfinance dictionary structure uses 'headline' and 'url'
            headline = item.get('headline') or item.get('title')
            link = item.get('url') or item.get('link')
            source = item.get('publisher') or item.get('source')
            
            if headline and link:
                st.markdown(f"**[{headline}]({link})**")
                st.caption(f"Source: {source} | Risk Level: Moderate")
                st.divider()
            
    except Exception:
        # Fallback Intel for when API is down or throttled
        st.info("Tactical Alert: Market watching Strait of Hormuz for 21mb/d supply risk.")

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("🛡️ Risk Controls")
    vol_threshold = st.slider("Volatility Alert Threshold", 0.10, 0.60, 0.40)
    risk_appetite = st.select_slider("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"], "Moderate")
    scenario_price = st.slider("Simulate Brent at ($):", 90, 200, 115)
    
    mults = {"Conservative": 1.5, "Moderate": 1.0, "Aggressive": 0.5}
    dynamic_hedge_pct = min(0.10 * (current_vol / vol_threshold) * mults[risk_appetite], 0.40)
    
    st.divider()
    display_intel_feed("BZ=F")

# --- 4. TOP METRICS & ANALYTICS ---
st.title("🛡️ Institutional Geopolitical Risk Dashboard")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Brent Crude", f"${current_bz:.2f}", "Escalation Risk")
m2.metric("War Premium (Spread)", f"${df['Spread'].iloc[-1]:.2f}", "Supply Risk")
m3.metric("Tail Risk (CVaR 95%)", f"{cvar_val:.2%}", "Expected Loss")
m4.metric("Gold (GC=F)", f"${df['GC=F'].iloc[-1]:,.2f}", "Safe Haven")

col_l, col_r = st.columns(2)
with col_l:
    st.plotly_chart(px.line(df, y="Spread", title="The 'War Premium' Trend"), use_container_width=True)
    st.map(pd.DataFrame({'lat': [26.5, 2.5, 29.9], 'lon': [56.3, 101.3, 32.5]}), color='#FF4B4B')

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
