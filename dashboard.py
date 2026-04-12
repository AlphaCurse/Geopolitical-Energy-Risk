import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIG & DATA ETL ---
st.set_page_config(page_title="Institutional Energy Risk", layout="wide")

@st.cache_data
def fetch_comprehensive_data():
    tickers = ["BZ=F", "CL=F", "GC=F", "ITA", "XOP"] # Brent, WTI, Gold, Defense, E&P
    df = yf.download(tickers, period="1y")['Close']
    df['Spread'] = df['BZ=F'] - df['CL=F']
    returns = df['BZ=F'].pct_change().dropna()
    
    # Advanced Metric: CVaR (Expected Shortfall) at 95%
    var_95 = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    
    return df, cvar_95

df, cvar_val = fetch_comprehensive_data()

# --- 2. SIDEBAR: INTEL & SETTINGS ---
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    risk_appetite = st.select_slider("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"])
    st.divider()
    st.subheader("📰 Live Intel Feed")
    st.caption("• [REUTERS] Israel-Iran war shock to flip market to deficit in 2026")
    st.caption("• [EIA] Strait of Hormuz chokepoint risks hitting 21mb/d")

# --- 3. TOP ROW: STRATEGIC PULSE ---
st.title("🛡️ Institutional Geopolitical Risk Dashboard")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Brent Crude", f"${df['BZ=F'].iloc[-1]:.2f}", "Escalation Risk")
c2.metric("War Premium (Spread)", f"${df['Spread'].iloc[-1]:.2f}")
c3.metric("Tail Risk (CVaR 95%)", f"{cvar_val:.2%}", "Expected Loss")
c4.metric("GPR Index", "Elevated (3.4)", "High Tension")

# --- 4. ALTERNATIVE DATA: SUPPLY CHOKEPOINTS ---
st.subheader("🌍 Alternative Data: Global Supply Chokepoints")
# Static mapping of chokepoints with risk levels (Dynamic proxies)
chokepoints = pd.DataFrame({
    'Name': ['Strait of Hormuz', 'Strait of Malacca', 'Suez Canal', 'Bab el-Mandeb'],
    'Lat': [26.5, 2.5, 29.9, 12.6],
    'Lon': [56.3, 101.3, 32.5, 43.3],
    'Status': ['Reduced Flow', 'Stable', 'Reduced Flow', 'High Risk']
})
st.map(chokepoints, latitude='Lat', longitude='Lon', size=20, color='#FF4B4B')

# --- 5. RISK & CORRELATION ANALYSIS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Cross-Asset Correlation")
    # Show how Gold/Defense move relative to Oil
    corr_matrix = df.pct_change().corr()
    fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r')
    st.plotly_chart(fig_corr, use_container_width=True)

with col_right:
    st.subheader("📉 Stress-Test Simulation")
    scenario_move = st.slider("Simulated Oil Spike (%)", 0, 100, 25)
    impact = scenario_move * cvar_val # Simple proxy impact
    st.write(f"Estimated Portfolio Impact of {scenario_move}% Spike: **{impact:.2%}**")
    st.progress(min(abs(impact), 1.0))
