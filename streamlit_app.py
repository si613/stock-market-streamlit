import streamlit as st
import yfinance as yf
import altair as alt
import plotly.graph_objects as go
import pandas as pd
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
def fetch_earnings(symbol):
    return yf.Ticker(symbol).earnings

@st.cache_data
def fetch_balance_sheet(symbol):
    return yf.Ticker(symbol).balance_sheet.T

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
    st.markdown(f"**Website:** [{information.get('website', '')}]({information.get('website', '')})")

    st.header('ℹ️ Interpretation Guide')
    st.markdown("""
    - **Company Info:** Overview of sector, size, and industry.
    - **Candlestick Charts:** Spot price trends and sentiment.
    - **Revenue & Income:** Financial performance over time.
    - **Dividends:** Track shareholder returns.
    - **Earnings Trends:** Compare historical earnings and revenue.
    - **Balance Sheet:** Understand company stability.
    """)

    # ✅ PRICE HISTORY + SAFE DATE FILTER
    price_history = fetch_weekly_price_history(symbol)
    min_date, max_date = price_history['Date'].min().date(), price_history['Date'].max().date()
    date_range = st.date_input("Select date range for price chart:", (min_date, max_date), min_value=min_date, max_value=max_date)

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
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
            decreasing_line_color='red'
        )
    ])
    candle_chart.update_layout(
        template="plotly_white",
        height=600,
        xaxis_rangeslider_visible=True,
        xaxis=dict(rangeselector=dict(
            buttons=[
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ]
        ))
    )
    st.plotly_chart(candle_chart, use_container_width=True)

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
            st.altair_chart(alt.Chart(df).mark_bar(color="#1f77b4").encode(
                x=alt.X(time_col, sort=None),
                y='Total Revenue'
            ).properties(height=300), use_container_width=True)

    with income_col:
        st.subheader("Net Income")
        if 'Net Income' in df.columns:
            st.altair_chart(alt.Chart(df).mark_bar(color="#ff7f0e").encode(
                x=alt.X(time_col, sort=None),
                y='Net Income'
            ).properties(height=300), use_container_width=True)

    st.header('💸 Dividends')
    dividends = fetch_dividends(symbol)
    if not dividends.empty:
        div_min, div_max = dividends['Date'].min().date(), dividends['Date'].max().date()
        div_range = st.date_input("Select dividend date range:", (div_min, div_max), min_value=div_min, max_value=div_max, key="dividends")

        if isinstance(div_range, tuple) and len(div_range) == 2:
            div_start = pd.to_datetime(div_range[0])
            div_end = pd.to_datetime(div_range[1])
            filtered_div = dividends[(dividends['Date'] >= div_start) & (dividends['Date'] <= div_end)]

            st.altair_chart(alt.Chart(filtered_div).mark_bar(color="#2ca02c").encode(
                x='Date:T',
                y='Dividends:Q'
            ).properties(height=300), use_container_width=True)
    else:
        st.write("No dividend data available.")

    st.header('📉 Earnings Performance')
    earnings = fetch_earnings(symbol)
    if earnings is not None and not earnings.empty:
        earnings = earnings.tail(5).reset_index()
        earnings_chart = alt.Chart(earnings).transform_fold(
            ['Earnings', 'Revenue'],
            as_=['Metric', 'Value']
        ).mark_line(point=True).encode(
            x='Year:T',
            y='Value:Q',
            color='Metric:N'
        ).properties(height=400)
        st.altair_chart(earnings_chart, use_container_width=True)
    else:
        st.write("No earnings data available.")

    st.header('📂 Balance Sheet Snapshot')
    balance = fetch_balance_sheet(symbol)
    if not balance.empty:
        balance = balance.tail(5).reset_index().rename(columns={'index': 'Date'})
        balance['Date'] = pd.to_datetime(balance['Date'], errors='coerce')
        balance = balance.dropna(subset=['Date'])
        key_cols = ['Total Assets', 'Total Liab', 'Total Stockholder Equity']
        available_cols = [col for col in key_cols if col in balance.columns]
        balance_long = balance.melt(id_vars='Date', value_vars=available_cols)
        st.altair_chart(alt.Chart(balance_long).mark_line(point=True).encode(
            x='Date:T',
            y='value:Q',
            color='variable:N'
        ).properties(height=400), use_container_width=True)
    else:
        st.write("No balance sheet data available.")
