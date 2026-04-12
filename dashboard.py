import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Institutional Energy Risk", layout="wide")

# --- 2. DATA ETL ---
@st.cache_data(ttl=3600)
def fetch_comprehensive_data():
    # Tickers: Brent, WTI, Gold, Defense (ITA)
    tickers = ["BZ=F", "CL=F", "GC=F", "ITA"] 
    df = yf.download(tickers, period="1y")['Close']
    
    # Transformations
    df['Spread'] = df['BZ=F'] - df['CL=F']
    returns = df['BZ=F'].pct_change().dropna()
    
    # Advanced Risk: CVaR (Expected Shortfall) at 95%
    var_95 = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    
    # Annualized Volatility for Hedge Logic
    df['Vol'] = returns.rolling(window=20).std() * np.sqrt(252)
    return df, cvar_95

df, cvar_val = fetch_comprehensive_data()
current_vol = df['Vol'].iloc[-1]
current_bz = df['BZ=F'].iloc[-1]

# --- 3. SIDEBAR: RISK CONTROLS & NEWS ---
with st.sidebar:
    st.header("🛡️ Risk Controls")
    vol_threshold = st.slider("Volatility Alert Threshold", 0.10, 0.60, 0.40)
    risk_appetite = st.select_slider("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"], "Moderate")
    scenario_price = st.slider("Simulate Brent at ($):", 90, 200, 115)
    
    # Dynamic Hedge Logic
    mults = {"Conservative": 1.5, "Moderate": 1.0, "Aggressive": 0.5}
    vol_ratio = current_vol / vol_threshold 
    dynamic_hedge_pct = min(0.10 * vol_ratio * mults[risk_appetite], 0.40)
    
    st.divider()
    st.subheader("📰 Real-Time Intel Feed")
    
    try:
        news_items = yf.Ticker("BZ=F").news[:5]
        if not news_items:
            st.info("Market Alert: Monitoring Strait of Hormuz for supply-chain bottlenecks.")
        else:
            for item in news_items:
                h = item.get('headline') or item.get('title') or "Energy Market Update"
                l = item.get('url') or item.get('link') or "#"
                st.markdown(f"**[{h}]({l})**")
                st.caption(f"Source: {item.get('publisher', 'Financial Feed')}")
                st.divider()
    except Exception:
        st.error("Intel Feed temporarily offline. Check Reuters Energy for live updates.")

# --- 4. TOP ROW: STRATEGIC PULSE ---
st.title("🛡️ Institutional Geopolitical Risk Dashboard")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Brent Crude", f"${current_bz:.2f}", "Escalation Risk")
m2.metric("War Premium (Spread)", f"${df['Spread'].iloc[-1]:.2f}", "Supply Risk")
m3.metric("Tail Risk (CVaR 95%)", f"{cvar_val:.2%}", "Expected Loss")
m4.metric("Gold (GC=F)", f"${df['GC=F'].iloc[-1]:,.2f}", "Safe Haven")

# --- 5. MAIN ANALYTICS AREA ---
col_l, col_r = st.columns(2)

with col_l:
    # Spread Chart
    st.plotly_chart(px.line(df, y="Spread", title="The 'War Premium' Trend"), use_container_width=True)
    
    # Supply Map
    st.subheader("🌍 Alternative Data: Global Chokepoints")
    chokepoints = pd.DataFrame({'lat': [26.5, 2.5, 29.9], 'lon': [56.3, 101.3, 32.5]})
    st.map(chokepoints, color='#FF4B4B')

with col_r:
    # Hedge Advisor
    st.subheader("🛡️ Dynamic Hedge Advisor")
    if current_vol > vol_threshold:
        st.error(f"CRITICAL VOLATILITY: {current_vol:.2%}")
        st.markdown(f"**Action:** Shift **{dynamic_hedge_pct:.1%}** to **Gold** & **Defense (ITA)**.")
        st.caption(f"Reasoning: Volatility is {vol_ratio:.1f}x your safety threshold.")
    else:
        st.success(f"STABLE VOLATILITY: {current_vol:.2%}")
    
    st.divider()
    
    # Scenario Stress Test
    st.subheader("📉 Scenario Stress Test")
    impact = (scenario_price - current_bz) / current_bz
    st.write(f"Estimated Impact at **${scenario_price}** Oil:")
    st.progress(min(abs(impact), 1.0))
    st.write(f"Unhedged Loss Estimate: **{impact:.2%}**")

st.caption("Data source: yFinance. Analysis calibrated for Israel-Iran geopolitical risk theater.")
