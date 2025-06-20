import streamlit as st
import yfinance as yf
import altair as alt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Stock Analysis Dashboard", initial_sidebar_state="expanded")

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
    ratios = {
        "PE Ratio": info.get("trailingPE", None),
        "PB Ratio": info.get("priceToBook", None),
        "Debt to Equity": info.get("debtToEquity", None),
        "Return on Equity": info.get("returnOnEquity", None),
        "Current Ratio": info.get("currentRatio", None),
    }
    return ratios

st.title('📊 Stock Market Analysis Dashboard')

symbol = st.text_input('Enter a stock symbol:', 'AAPL')

if symbol:
    ticker = yf.Ticker(symbol)
    information = fetch_stock_info(symbol)
    st.header('🏢 Company Information')
    st.markdown(f"**Name:** {information.get('longName', 'N/A')}")
    st.markdown(f"**Sector:** {information.get('sector', 'N/A')}")
    st.markdown(f"**Industry:** {information.get('industry', 'N/A')}")
    st.markdown(f"**Market Cap:** {information.get('marketCap', 0):,}")
    st.markdown(f"**Currency:** {information.get('currency', 'N/A')}")
    st.markdown(f"**Website:** [{information.get('website', '')}]({information.get('website', '')})")

    st.subheader("📌 Interpretation Guide")
    st.markdown("""
    **Company Information** tells you about the business size, sector, and industry. The currency is the one in which the stock trades. A larger market cap typically means a more established company.
    """)

    price_history = fetch_weekly_price_history(symbol)
    price_history['Date'] = pd.to_datetime(price_history['Date'], errors='coerce')
    min_date, max_date = price_history['Date'].min(), price_history['Date'].max()
    date_range = st.date_input("Select date range for price chart:", (min_date.date(), max_date.date()), min_value=min_date.date(), max_value=max_date.date())

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0], utc=True)
        end_date = pd.to_datetime(date_range[1], utc=True)
        filtered_price = price_history[(price_history['Date'] >= start_date) & (price_history['Date'] <= end_date)]
    else:
        st.error("Please select a valid date range.")
        st.stop()

    st.header('📈 Price History & Candlestick Chart')
    candle_chart = go.Figure(data=[
        go.Candlestick(
            x=filtered_price['Date'],
            open=filtered_price['Open'],
            high=filtered_price['High'],
            low=filtered_price['Low'],
            close=filtered_price['Close'],
            increasing_line_color='green',
            decreasing_line_color='red')])
    candle_chart.update_layout(template="plotly_white", height=600, xaxis_rangeslider_visible=True)
    st.plotly_chart(candle_chart, use_container_width=True)

    st.subheader("📌 Interpretation Guide")
    st.markdown("""
    **Candlestick Chart** shows price action per week. Green candles indicate price increases; red candles show decreases.
    """)

    st.subheader("📉 Moving Average, RSI & MFI")
    filtered_price['MA20'] = filtered_price['Close'].rolling(window=20).mean()
    filtered_price['MA50'] = filtered_price['Close'].rolling(window=50).mean()

    delta = filtered_price['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    filtered_price['RSI'] = 100 - (100 / (1 + rs))

    typical_price = (filtered_price['High'] + filtered_price['Low'] + filtered_price['Close']) / 3
    money_flow = typical_price * filtered_price['Volume']
    pos_flow = money_flow.where(delta > 0, 0).rolling(14).sum()
    neg_flow = money_flow.where(delta < 0, 0).rolling(14).sum()
    mfi = 100 * (pos_flow / (pos_flow + neg_flow))
    filtered_price['MFI'] = mfi

    ma_fig = go.Figure()
    ma_fig.add_trace(go.Scatter(x=filtered_price['Date'], y=filtered_price['Close'], mode='lines', name='Close'))
    ma_fig.add_trace(go.Scatter(x=filtered_price['Date'], y=filtered_price['MA20'], mode='lines', name='MA20'))
    ma_fig.add_trace(go.Scatter(x=filtered_price['Date'], y=filtered_price['MA50'], mode='lines', name='MA50'))
    ma_fig.update_layout(title='Moving Averages', template='plotly_white')
    st.plotly_chart(ma_fig, use_container_width=True)

    rsi_fig = go.Figure(go.Scatter(x=filtered_price['Date'], y=filtered_price['RSI'], mode='lines', name='RSI'))
    rsi_fig.update_layout(title='Relative Strength Index (RSI)', yaxis=dict(range=[0, 100]), template='plotly_white')
    st.plotly_chart(rsi_fig, use_container_width=True)

    mfi_fig = go.Figure(go.Scatter(x=filtered_price['Date'], y=filtered_price['MFI'], mode='lines', name='MFI'))
    mfi_fig.update_layout(title='Money Flow Index (MFI)', yaxis=dict(range=[0, 100]), template='plotly_white')
    st.plotly_chart(mfi_fig, use_container_width=True)

    st.subheader("📌 Interpretation Guide")
    st.markdown("""
    **Moving Averages** smooth out price data to show trends. A rising MA suggests uptrend.

    **RSI (Relative Strength Index)** indicates momentum. RSI > 70 = overbought, < 30 = oversold.

    **MFI (Money Flow Index)** considers both price and volume. MFI > 80 = overbought, < 20 = oversold.
    """)

    st.header('📊 Financial Performance')
    selection = st.radio("Select Financial View:", ['Quarterly', 'Annual'], horizontal=True)
    if selection == 'Quarterly':
        df = fetch_quarterly_financials(symbol).rename_axis('Quarter').reset_index()
        df['Quarter'] = df['Quarter'].astype(str)
    else:
        df = fetch_annual_financials(symbol).rename_axis('Year').reset_index()
        df['Year'] = df['Year'].astype(str).str[:4]

    time_col = df.columns[0]
    revenue_col, income_col = st.columns(2)
    with revenue_col:
        st.subheader("Total Revenue")
        if 'Total Revenue' in df.columns:
            st.altair_chart(alt.Chart(df).mark_bar(color="#1f77b4").encode(x=alt.X(time_col, sort=None), y='Total Revenue').properties(height=300), use_container_width=True)
    with income_col:
        st.subheader("Net Income")
        if 'Net Income' in df.columns:
            st.altair_chart(alt.Chart(df).mark_bar(color="#ff7f0e").encode(x=alt.X(time_col, sort=None), y='Net Income').properties(height=300), use_container_width=True)

    st.subheader("📌 Interpretation Guide")
    st.markdown("""
    **Revenue** is total sales. **Net Income** is what's left after all costs. Growth in these over time usually means a healthy business.
    """)

    st.header('💸 Dividends')
    dividends = fetch_dividends(symbol)
    if not dividends.empty:
        div_min, div_max = dividends['Date'].min(), dividends['Date'].max()
        div_range = st.date_input("Select dividend date range:", (div_min.date(), div_max.date()), min_value=div_min.date(), max_value=div_max.date(), key="dividends")
        if isinstance(div_range, tuple) and len(div_range) == 2:
            div_start = pd.to_datetime(div_range[0], utc=True)
            div_end = pd.to_datetime(div_range[1], utc=True)
            filtered_div = dividends[(dividends['Date'] >= div_start) & (dividends['Date'] <= div_end)]
            st.altair_chart(alt.Chart(filtered_div).mark_bar(color="#2ca02c").encode(x='Date:T', y='Dividends:Q').properties(height=300), use_container_width=True)
    else:
        st.write("No dividend data available.")

    st.subheader("📌 Interpretation Guide")
    st.markdown("""
    **Dividends** are company payouts to shareholders. Frequent and growing dividends may signal financial health.
    """)

    st.header('📂 Balance Sheet Snapshot')
    balance = fetch_balance_sheet(symbol)
    if not balance.empty:
        balance = balance.tail(4).reset_index().rename(columns={'index': 'Date'})
        balance['Date'] = pd.to_datetime(balance['Date'], errors='coerce')
        balance = balance.dropna(subset=['Date'])
        key_cols = ['Total Assets', 'Total Liab', 'Total Stockholder Equity']
        available_cols = [col for col in key_cols if col in balance.columns]
        balance_long = balance.melt(id_vars='Date', value_vars=available_cols)
        st.altair_chart(alt.Chart(balance_long).mark_line(point=True).encode(x='Date:T', y='value:Q', color='variable:N').properties(height=400), use_container_width=True)

    st.subheader("📌 Interpretation Guide")
    st.markdown("""
    **Balance Sheet** shows company assets vs. liabilities. Healthy equity (assets - liabilities) is a good sign.
    """)

    st.header("📐 Key Ratios")
    ratios = fetch_key_ratios(symbol)
    for k, v in ratios.items():
        st.markdown(f"**{k}:** {v if v is not None else 'N/A'}")

    st.subheader("📌 Interpretation Guide")
    st.markdown("""
    - **PE Ratio:** High may mean overvalued; low may mean undervalued.
    - **PB Ratio:** Compares market to book value; < 1 might mean undervaluation.
    - **Debt to Equity:** Shows leverage. High ratio = more debt.
    - **Return on Equity:** Profitability. Higher = better.
    - **Current Ratio:** Liquidity. >1 means it can cover short-term debts.
    """)
