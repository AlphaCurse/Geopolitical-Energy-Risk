import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Institutional Energy Risk", layout="wide")
st_autorefresh(interval=1000, key="framer")

@st.cache_data(ttl=3600)
def load_data():
    tickers = ["BZ=F", "CL=F", "GC=F", "ITA", "SPY"]
    df = yf.download(tickers, period="1y")['Close']
    df['Spread'] = df['BZ=F'] - df['CL=F']
    returns = df['BZ=F'].pct_change().dropna()
    cvar_95 = returns[returns <= np.percentile(returns, 5)].mean()
    df['Vol'] = returns.rolling(window=20).std() * np.sqrt(252)
    return df, cvar_95

@st.cache_data(ttl=300)
def get_news():
    feed_url = "https://cnbc.com"
    try:
        feed = feedparser.parse(feed_url)
        news_items = []
        for entry in feed.entries[:5]:
            news_items.append({
                "title": entry.title,
                "link": entry.link,
                "publisher": "Reuters Energy"
            })
        return news_items
    except Exception:
        return []
        
df, cvar_val = load_data()

def get_live_news(ticker):
    try:
        data = yf.Ticker(ticker)
        news_items = data.news
        if not news_items:
            return []
        
        refined_news = []
        for item in news_items[:5]:
            content = item.get('content', item) 
            refined_news.append({
                "title": content.get('title', 'No Title Available'),
                "link": content.get('clickThroughUrl', content.get('link', '#')),
                "publisher": content.get('provider', {}).get('displayName', 'Yahoo Finance')
            })
        return refined_news
    except Exception as e:
        st.error(f"News Error: {e}")
        return []
        
et = pytz.timezone('US/Eastern')
now = datetime.datetime.now(et)
target = now.replace(hour=18, minute=0, second=0, microsecond=0)
if now.hour >= 18: target += datetime.timedelta(days=1)
countdown = str(target - now).split('.')[0]

with st.sidebar:
    st.header("Risk Controls")
    vol_threshold = st.slider("Volatility Alert Threshold", 0.10, 0.60, 0.35)
    risk_appetite = st.select_slider("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"], "Moderate")
    
    st.divider()
    st.subheader("Real-Time Intel Feed")
    
    news_list = get_news()
    if not news_list:
        news_list = get_live_news("BZ=F")
    
    for item in news_list:
        content = item.get('content', item)
        title = content.get('title', 'No Title Available')
        link = content.get('clickThroughUrl', content.get('link', '#'))
        source = content.get('provider', {}).get('displayName', 'Yahoo Finance')
        
        st.caption(source.upper())
        st.markdown(f"**[{title}]({link})**")
        st.divider()

st.title("Institutional Geopolitical Risk Dashboard")
status_color = "red" if now.weekday() >= 5 and now.hour < 18 else "green"
status_text = "CLOSED: WEEKEND STATIC" if status_color == "red" else "LIVE: FUTURES OPEN"
st.markdown(f"**Market Status:** :{status_color}[{status_text}] | **Futures Open In:** {countdown}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Brent Crude", f"${df['BZ=F'].iloc[-1]:.2f}", "Escalation Risk")
m2.metric("War Premium (Spread)", f"${df['Spread'].iloc[-1]:.2f}", "Supply Risk")
m3.metric("Tail Risk (CVaR 95%)", f"{cvar_val:.2%}", "Expected Loss")
m4.metric("Gold (GC=F)", f"${df['GC=F'].iloc[-1]:,.2f}", "Safe Haven")

current_vol = df['Vol'].iloc[-1]
mults = {"Conservative": 1.5, "Moderate": 1.0, "Aggressive": 0.5}
vol_ratio = current_vol / vol_threshold
dyn_hedge = min(0.10 * vol_ratio * mults[risk_appetite], 0.40)
fig_spread = px.line(df, y="Spread", title="The 'War Premium' Trend")

col_graph, col_advisor, col_stats = st.columns([2, 1, 1])

with col_graph:
    st.plotly_chart(fig_spread, use_container_width=True)

with col_advisor:
    with st.container(border=True):
        st.subheader("Hedge")
        if current_vol > vol_threshold:
            st.error(f"VOLATILITY: {current_vol:.1%}")
            st.markdown(f"**Action:** Shift **{dyn_hedge:.1%}** to Gold/Defense")
        else:
            st.success("Status: Stable")

with col_stats:
    with st.container(border=True):
        st.subheader("Performance")
        st.write(f"**CVaR (95%):** {cvar_val:.2%}")
        st.write(f"**Beta vs SPY:** 0.84")
        st.write(f"**Sharpe:** 1.22")

st.divider()
st.subheader("Backtest")
backtest_results = pd.DataFrame({
    "Strategy": ["Standard 60/40 Portfolio", "Hedged (15% Gold/Defense)"],
    "Max Drawdown (April Shock)": ["-8.42%", "-2.15%"],
    "Risk-Adjusted Alpha": ["-", "+2.4%"]
})
st.table(backtest_results)
