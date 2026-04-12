import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. CONFIG & DATA ETL ---
st.set_page_config(page_title="Institutional Energy Risk", layout="wide")

def display_live_intel(ticker):
    st.subheader("📰 Real-Time Geopolitical Intelligence")
    news_items = yf.Ticker(ticker).news[:5] # Get top 5 stories
    for item in news_items:
        with st.container():
            st.markdown(f"**[{item['title']}]({item['link']})**")
            st.caption(f"Source: {item['publisher']} | Related Tickers: {', '.join(item['relatedTickers'])}")
            st.divider()

@st.cache_data
def fetch_comprehensive_data():
    # Tickers: Brent, WTI, Gold, Defense, E&P
    tickers = ["BZ=F", "CL=F", "GC=F", "ITA", "XOP"] 
    df = yf.download(tickers, period="1y")['Close']
    df['Spread'] = df['BZ=F'] - df['CL=F']
    returns = df['BZ=F'].pct_change().dropna()
    
    # Advanced Risk: CVaR (Expected Shortfall) at 95%
    var_95 = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    
    # Volatility for the Hedge Logic
    df['Vol'] = returns.rolling(window=20).std() * np.sqrt(252)
    
    return df, cvar_95

df, cvar_val = fetch_comprehensive_data()
current_vol = df['Vol'].iloc[-1]

# --- 2. SIDEBAR: RISK CONTROLS ---
with st.sidebar:
    st.header("🛡️ Hedge & Risk Controls")
    vol_threshold = st.slider("Volatility Alert Threshold", 0.10, 0.60, 0.40)
    risk_appetite = st.select_slider("Risk Tolerance", options=["Conservative", "Moderate", "Aggressive"], value="Moderate")
    
    st.divider()
    st.subheader("War Escalation Simulator")
    scenario_price = st.slider("Simulate Brent Crude at ($):", 90, 200, 115)
    
    # RE-INSTATED: Dynamic Hedge Logic
    baseline_hedge = 0.10
    multipliers = {"Conservative": 1.5, "Moderate": 1.0, "Aggressive": 0.5}
    vol_ratio = current_vol / vol_threshold 
    dynamic_hedge_pct = min(baseline_hedge * vol_ratio * multipliers[risk_appetite], 0.40)

# --- 3. TOP ROW: KEY METRICS ---
st.title("🛡️ Institutional Geopolitical Risk Dashboard")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Brent Crude", f"${df['BZ=F'].iloc[-1]:.2f}", "Escalation Risk")
m2.metric("War Premium (Spread)", f"${df['Spread'].iloc[-1]:.2f}")
m3.metric("Tail Risk (CVaR 95%)", f"{cvar_val:.2%}", "Expected Loss")
m4.metric("Gold (GC=F)", f"${df['GC=F'].iloc[-1]:,.2f}", "Safe Haven")

# --- 4. MAIN ANALYTICS AREA ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.plotly_chart(px.line(df, y="Spread", title="The 'War Premium' (Brent-WTI Spread)"), use_container_width=True)
    
    st.subheader("🌍 Supply Chokepoints")
    chokepoints = pd.DataFrame({
        'Name': ['Strait of Hormuz', 'Strait of Malacca', 'Suez Canal'],
        'lat': [26.5, 2.5, 29.9], 'lon': [56.3, 101.3, 32.5]
    })
    st.map(chokepoints, color='#FF4B4B')

with col_right:
    # THE RE-INSTATED HEDGE ADVISOR
    st.subheader("🛡️ Dynamic Hedge Advisor")
    display_live_intel("BZ=F")
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
    projected_impact = (scenario_price - df['BZ=F'].iloc[-1]) / df['BZ=F'].iloc[-1]
    st.write(f"Estimated Impact at **${scenario_price}** Oil:")
    st.progress(min(abs(projected_impact), 1.0))
    st.write(f"Unhedged Loss Estimate: **{projected_impact:.2%}**")

st.caption("Data source: yFinance. CVaR (Expected Shortfall) calculated at 95% confidence.")
