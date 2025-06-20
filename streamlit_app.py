import streamlit as st
import yfinance as yf
import altair as alt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Stock Analysis Dashboard", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    body {
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def fetch_stock_info(symbol):
    return yf.Ticker(symbol).info

@st.cache_data
def fetch_quarterly_financials(symbol):
    return yf.Ticker(symbol).quarterly_financials.T

@st.cache_data
def fetch_annual_financials(symbol):
    return yf.Ticker(symbol).financials.T

@st.cache_data
def fetch_weekly_price_history(symbol):
    hist = yf.Ticker(symbol).history(period='5y', interval='1wk').reset_index()
    hist['Date'] = pd.to_datetime(hist['Date'], errors='coerce')
    return hist.dropna(subset=['Date'])

@st.cache_data
def fetch_dividends(symbol):
    div = yf.Ticker(symbol).dividends.reset_index()
    div['Date'] = pd.to_datetime(div['Date'], errors='coerce')
    return div.dropna(subset=['Date'])

@st.cache_data
def fetch_balance_sheet(symbol):
    return yf.Ticker(symbol).balance_sheet.T

@st.cache_data
def fetch_key_ratios(symbol):
    info = fetch_stock_info(symbol)
    return {
        "PE Ratio": info.get("trailingPE"),
        "PB Ratio": info.get("priceToBook"),
        "Debt to Equity": info.get("debtToEquity"),
        "Return on Equity": info.get("returnOnEquity"),
        "Current Ratio": info.get("currentRatio"),
    }

st.title('📊 Stock Market Analysis Dashboard')

symbol = st.text_input('Enter a stock symbol:', 'AAPL')

if symbol:
    ticker = yf.Ticker(symbol)
    info = fetch_stock_info(symbol)
    st.header('🏢 Company Information')
    st.markdown(f"**Name:** {info.get('longName', 'N/A')}")
    st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
    st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
    st.markdown(f"**Currency:** {info.get('currency', 'N/A')}")
    st.markdown(f"**Market Cap:** {info.get('marketCap', 0):,}")
    st.markdown(f"**Website:** [{info.get('website', '')}]({info.get('website', '')})")

    st.subheader("📘 Interpretation Guide")
    st.markdown("""These details give you a quick snapshot of what the company does, what sector it operates in, and the currency in which it's traded.""")

    price = fetch_weekly_price_history(symbol)
    price['MA20'] = price['Close'].rolling(window=20).mean()
    price['MA50'] = price['Close'].rolling(window=50).mean()

    delta = price['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    price['RSI'] = 100 - (100 / (1 + rs))

    typical_price = (price['High'] + price['Low'] + price['Close']) / 3
    money_flow = typical_price * price['Volume']
    pos_flow = money_flow.where(delta > 0, 0).rolling(14).sum()
    neg_flow = money_flow.where(delta < 0, 0).rolling(14).sum()
    price['MFI'] = 100 * (pos_flow / (pos_flow + neg_flow))

    min_date, max_date = price['Date'].min(), price['Date'].max()
    date_range = st.date_input("Select date range:", (min_date.date(), max_date.date()), min_value=min_date.date(), max_value=max_date.date())

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0], utc=True)
        end_date = pd.to_datetime(date_range[1], utc=True)
        price = price[(price['Date'] >= start_date) & (price['Date'] <= end_date)]

    st.header('📈 Candlestick Chart + Moving Averages')
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=price['Date'], open=price['Open'], high=price['High'], low=price['Low'], close=price['Close'],
        increasing_line_color='green', decreasing_line_color='red', name='Candlestick'))
    fig.add_trace(go.Scatter(x=price['Date'], y=price['MA20'], mode='lines', name='MA20', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=price['Date'], y=price['MA50'], mode='lines', name='MA50', line=dict(color='orange')))
    fig.update_layout(template="plotly_white", height=600, xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📘 Interpretation Guide")
    st.markdown("""MA lines smooth out price to highlight trends. RSI below 30 may mean oversold; above 70, overbought. MFI adds volume into the mix for stronger signals.""")

    st.header('📉 RSI and MFI Charts')
    st.line_chart(price.set_index('Date')[['RSI']])
    st.line_chart(price.set_index('Date')[['MFI']])

    st.header('📊 Key Financial Ratios')
    ratios = fetch_key_ratios(symbol)
    st.dataframe(pd.DataFrame(ratios.items(), columns=['Metric', 'Value']).set_index('Metric'))

    st.subheader("📘 Interpretation Guide")
    st.markdown("""These ratios reflect the company's valuation and financial strength. Lower PE can indicate undervaluation; ROE shows profitability; debt/equity indicates leverage.""")

    st.header('📊 Financial Performance')
    view = st.radio("Select View:", ["Quarterly", "Annual"], horizontal=True)
    if view == 'Quarterly':
        fin = fetch_quarterly_financials(symbol).rename_axis('Quarter').reset_index()
    else:
        fin = fetch_annual_financials(symbol).rename_axis('Year').reset_index()
        fin[fin.columns[0]] = fin[fin.columns[0]].astype(str).str[:4]

    time_col = fin.columns[0]
    cols = st.columns(2)
    with cols[0]:
        st.subheader("Total Revenue")
        if 'Total Revenue' in fin.columns:
            st.altair_chart(alt.Chart(fin).mark_bar(color="#1f77b4").encode(x=alt.X(time_col, sort=None), y='Total Revenue').properties(height=300), use_container_width=True)
    with cols[1]:
        st.subheader("Net Income")
        if 'Net Income' in fin.columns:
            st.altair_chart(alt.Chart(fin).mark_bar(color="#ff7f0e").encode(x=alt.X(time_col, sort=None), y='Net Income').properties(height=300), use_container_width=True)

    st.subheader("📘 Interpretation Guide")
    st.markdown("""Track how revenue and income evolve. Declines may signal trouble; growth shows strength.""")

    st.header('💸 Dividends')
    div = fetch_dividends(symbol)
    if not div.empty:
        div_min, div_max = div['Date'].min(), div['Date'].max()
        div_range = st.date_input("Select dividend date range:", (div_min.date(), div_max.date()), min_value=div_min.date(), max_value=div_max.date(), key="div")
        if isinstance(div_range, tuple) and len(div_range) == 2:
            div = div[(div['Date'] >= pd.to_datetime(div_range[0], utc=True)) & (div['Date'] <= pd.to_datetime(div_range[1], utc=True))]
            st.altair_chart(alt.Chart(div).mark_bar(color="#2ca02c").encode(x='Date:T', y='Dividends:Q').properties(height=300), use_container_width=True)
    else:
        st.write("No dividend data available.")

    st.subheader("📘 Interpretation Guide")
    st.markdown("""Dividends reward shareholders. Consistent or growing dividends reflect financial health and shareholder commitment.""")

    st.header('📂 Balance Sheet Snapshot')
    bal = fetch_balance_sheet(symbol)
    if not bal.empty:
        bal = bal.tail(4).reset_index().rename(columns={'index': 'Date'})
        bal['Date'] = pd.to_datetime(bal['Date'], errors='coerce')
        bal = bal.dropna(subset=['Date'])
        key_cols = ['Total Assets', 'Total Liab', 'Total Stockholder Equity']
        available = [col for col in key_cols if col in bal.columns]
        bal_melt = bal.melt(id_vars='Date', value_vars=available)
        st.altair_chart(alt.Chart(bal_melt).mark_line(point=True).encode(x='Date:T', y='value:Q', color='variable:N').properties(height=400), use_container_width=True)

    st.subheader("📘 Interpretation Guide")
    st.markdown("""A healthy balance sheet shows more assets than liabilities. Equity should ideally be growing over time.""")
