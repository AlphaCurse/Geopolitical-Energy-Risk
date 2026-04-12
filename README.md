# Institutional Geopolitical Energy Risk Dashboard

A real-time analytics suite designed to monitor energy market volatility and geopolitical supply risks. This dashboard calculates the **"War Premium"** and provides dynamic hedging recommendations based on institutional tail-risk metrics.

**Live Dashboard:** [[Geopolitical Energy Risk Dashboard](https://geopolitical-energy-risk-dashboard.streamlit.app/)]

## 🚀 Key Features
*   **The 'War Premium' Tracker:** Monitors the spread between Brent Crude (Global) and WTI (Domestic) to quantify regional escalation and supply-chain risks.
*   **Tail Risk (CVaR 95%):** Calculates "Expected Shortfall" during extreme market events, providing a deeper look at risk than standard volatility.
*   **Dynamic Hedge Advisor:** Generates automated portfolio reallocation signals for Gold and Defense (ITA) based on real-time volatility thresholds.
*   **Live Intel Feed:** Integrated RSS stream providing real-time situational awareness from global energy news desks.
*   **Automated Market Status:** Real-time countdown to CME/NYMEX futures sessions and weekend/live status indicators.

## 📊 Methodology
*   **Volatility Logic:** Utilizes a 20-day rolling window scaled for annualized volatility to trigger risk alerts.
*   **Hedge Ratio:** A weighted multiplier system that adjusts recommendations based on user-defined risk appetites (Conservative, Moderate, Aggressive).
*   **Data Integrity:** Multi-source data pipeline utilizing `yfinance` for market pricing and `feedparser` for asynchronous news retrieval.

## 🛠️ Tech Stack
*   **Language:** Python
*   **Frontend:** Streamlit
*   **Visualizations:** Plotly Express
*   **Financial Data:** Yahoo Finance API
*   **Intelligence:** RSS/XML parsing (Reuters Energy)
