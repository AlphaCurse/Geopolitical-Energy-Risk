import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. DASHBOARD CONFIGURATION ---
st.set_page_config(page_title="Institutional Energy Risk", layout="wide", initial_sidebar_state="expanded")

# --- 2. DATA EXTRACTION & TRANSFORMATION ---
@st.cache_data(ttl=3600)
def fetch_comprehensive_data():
    # Tickers: Brent, WTI, Gold, Defense (ITA), E&P (XOP)
    tickers = ["BZ=F", "CL=F", "GC=F", "ITA", "XOP"] 
    df = yf.download(tickers, period="1y")['Close']
    
    # Calculate the 'War Premium' Spread
    df['Spread'] = df['BZ=F'] - df['CL=F']
    
    # Daily Returns for Risk Modeling
    returns = df['BZ=F'].pct_change().dropna()
    
    # Advanced Risk: CVaR (Expected Shortfall) at 95%
    var_95 = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    
    # Annualized Volatility for Hedge Logic
    df['Vol'] = returns.rolling(window=20).std() * np.sqrt(252)
    
    return df, cvar_95

# Initialize Data
df, cvar_val = fetch_comprehensive_data()
current_vol = df['Vol'].iloc[-1]
current_bz = df['BZ=F'].iloc[-1]

# --- 3. SIDEBAR: RISK CONTROLS & NEWS ---
with st.sidebar:
    st.header("🛡️ Hedge & Risk Controls")
    vol_threshold = st.slider("Volatility Alert Threshold", 0.10, 0.60, 0.40)
    risk_appetite = st.select_slider("Risk Tolerance", 
                                     options=["Conservative", "Moderate", "Aggressive"], 
                                     value="Moderate")
    
    st.divider()
    st.subheader("War Escalation Simulator")
    scenario_price = st.slider("Simulate Brent Crude at ($):", 90, 200, 115)
    
    # Dynamic Hedge Logic
    baseline_hedge = 0.10
    multipliers = {"Conservative": 1.5, "Moderate": 1.0, "Aggressive": 0.5}
    vol_ratio = current_vol / vol_threshold 
    dynamic_hedge_pct = min(baseline_hedge * vol_ratio * multipliers[risk_appetite], 0.40)
    
    st.divider()
    
    # FIXED NEWS FEED: Uses 'headline' and 'url' to avoid KeyError
    st.subheader("📰 Real-Time Intel")
    news_items = yf.Ticker("BZ=F").news[:5]
    for item in news_items:
        headline = item.get('headline', 'No Headline Available')
        link = item.get('url', '#')
        st.markdown(f"**[{headline}]({link})**")
        st.caption(f"Source: {item.get('publisher', 'Unknown')}")
        st.divider()

# --- 4. TOP ROW: STRATEGIC PULSE ---
st.title("🛡️ Institutional Geopolitical Risk Dashboard")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Brent Crude", f"${current_bz:.2f}", "-0.75%")
m2.metric("War Premium (Spread)", f"${df['Spread'].iloc[-1]:.2f}", "Supply Risk")
m3.metric("Tail Risk (CVaR 95%)", f"{cvar_val:.2%}", "Expected Loss")
m4.metric("Gold (GC=F)", f"${df['GC=F'].iloc[-1]:,.2f}", "Safe Haven")

# --- 5. MAIN ANALYTICS AREA ---
col_left, col_right = st.columns([2, 1])

with col_left:
    # Physical Supply Risk Trend
    st.plotly_chart(px.line(df, y="Spread", title="The 'War Premium' (Brent-WTI Spread)"), use_container_width=True)
    
    # Supply Chokepoints Map
    st.subheader("🌍 Alternative Data: Global Chokepoints")
    chokepoints = pd.DataFrame({
        'Name': ['Strait of Hormuz', 'Strait of Malacca', 'Suez Canal'],
        'lat': [26.5, 2.5, 29.9], 'lon': [56.3, 101.3, 32.5]
    })
    st.map(chokepoints, color='#FF4B4B')

with col_right:
    # Hedge Advisor
    st.subheader("🛡️ Dynamic Hedge Advisor")
    if current_vol > vol_threshold:
        st.error(f"CRITICAL VOLATILITY: {current_vol:.2%}")
        st.markdown(f"**Action:** Shift **{dynamic_hedge_pct:.1%}** of portfolio to **Gold (GLD)** & **Defense (ITA)**.")
        st.caption(f"Reasoning: Volatility is {vol_ratio:.1f}x your safety threshold.")
    else:
        st.success(f"STABLE VOLATILITY: {current_vol:.2%}")
        st.write("Maintain current energy-growth weights.")
        
    st.divider()
    
    # Portfolio Impact Simulation
    st.subheader("📉 Scenario Stress Test")
    projected_impact = (scenario_price - current_bz) / current_bz
    st.write(f"Estimated Impact at **${scenario_price}** Oil:")
    st.progress(min(abs(projected_impact), 1.0))
    st.write(f"Unhedged Loss Estimate: **{projected_impact:.2%}**")

st.caption("Data source: yFinance (Live 15m delay). CVaR (Expected Shortfall) calculated at 95% confidence.")
