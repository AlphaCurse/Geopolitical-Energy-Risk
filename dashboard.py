import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. DASHBOARD CONFIGURATION ---
st.set_page_config(page_title="Geopolitical Energy Risk", layout="wide", initial_sidebar_state="expanded")

# --- 2. SIDEBAR: RISK CONTROLS & SCENARIO INPUTS ---
with st.sidebar:
    st.header("Hedge & Risk Controls")
    vol_threshold = st.slider("Volatility Alert Threshold", 0.10, 0.60, 0.40)
    st.divider()
    
    st.subheader("War Escalation Simulator")
    scenario_price = st.slider("Simulate Brent Crude at ($):", 90, 200, 115)
    st.caption("EIA projects peaks of $115/b in Q2 2026 if supply shut-ins persist.")

    risk_appetite = st.sidebar.select_slider("Risk Tolerance", options=["Conservative", "Moderate", "Aggressive"], value="Moderate")
    multipliers = {"Conservative": 1.5, "Moderate": 1.0, "Aggressive": 0.5}
    dynamic_hedge_pct = min(baseline_hedge * vol_ratio * multipliers[risk_appetite], 0.40)
    
# --- 3. ETL: DATA EXTRACTION & TRANSFORMATION ---
@st.cache_data(ttl=3600)
def fetch_risk_data():
    tickers = ["BZ=F", "CL=F", "GC=F", "ITA"] # Brent, WTI, Gold, Defense ETF
    raw_data = yf.download(tickers, period="1y")['Close']
    
    # Transformations
    raw_data['Spread'] = raw_data['BZ=F'] - raw_data['CL=F'] # 'War Premium'
    returns = raw_data['BZ=F'].pct_change()
    raw_data['Vol'] = returns.rolling(window=20).std() * np.sqrt(252)
    return raw_data

df = fetch_risk_data()
current_bz = df['BZ=F'].iloc[-1]
current_vol = df['Vol'].iloc[-1]

# --- 4. TOP ROW: KEY RISK METRICS ---
st.title("Energy Risk Dashboard: Israel-Iran Conflict")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Brent Crude", f"${current_bz:.2f}", "-0.75%")
m2.metric("Brent-WTI Spread", f"${df['Spread'].iloc[-1]:.2f}", "Supply Risk")
m3.metric("Gold (GC=F)", f"${df['GC=F'].iloc[-1]:,.2f}", "Safe Haven")
m4.metric("Defense (ITA)", f"${df['ITA'].iloc[-1]:.2f}", "Sector Hedge")

# --- 5. MAIN ANALYTICS AREA ---
left_col, right_col = st.columns([2, 1])

with left_col:
    # Physical Supply Risk Visualization
    fig = px.line(df, y="Spread", title="The 'War Premium' (Brent-WTI Spread Trend)")
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📄 Geopolitical Intel: Latest Escalations"):
        st.write("**April 12, 2026**: Peace talks in Islamabad fail; US threatens Strait of Hormuz blockade.")
        st.write("**April 10, 2026**: Brent falls to $95.20 following a fragile ceasefire announcement.")

# --- Dynamic Hedge Logic ---
baseline_hedge = 0.10  # 10% base hedge
# Ratio of how much we are over the threshold
vol_ratio = current_vol / vol_threshold 

# Dynamic percentage (capped at 30% for safety)
dynamic_hedge_pct = min(baseline_hedge * vol_ratio, 0.30) 

with right_col:
    st.subheader("Dynamic Hedge Advisor")
    if current_vol > vol_threshold:
        st.error(f"CRITICAL VOLATILITY: {current_vol:.2%}")
        st.markdown(f"**Action:** Shift **{dynamic_hedge_pct:.1%}** of portfolio to **Gold** & **Defense (ITA)**.")
        st.caption(f"Reasoning: Volatility is {vol_ratio:.1f}x your safety threshold.")
    else:
        st.success(f"STABLE VOLATILITY: {current_vol:.2%}")
        st.write("Maintain current energy-growth weights.")
        
    st.divider()
    
    # Portfolio Impact Simulation
    st.subheader("📉 Scenario Stress Test")
    projected_impact = (scenario_price - current_bz) / current_bz
    st.write(f"Estimated Portfolio Impact at **${scenario_price}** Oil:")
    st.progress(min(abs(projected_impact), 1.0))
    st.write(f"Unhedged Loss Estimate: **{projected_impact:.2%}**")

# --- 6. FOOTER & DATA SOURCE ---
st.caption("Data source: yFinance (Live 15m delay). Scenarios based on EIA Short-Term Energy Outlook.")
