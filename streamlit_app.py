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
    hist = yf.Ticker(symbol).history(period='5y', interval='1wk')
    hist = hist.reset_index()
    hist['Date'] = pd.to_datetime(hist['Date'], errors='coerce')
    return hist.dropna(subset=['Date'])

@st.cache_data
def fetch_dividends(symbol):
    div = yf.Ticker(symbol).dividends
    div = div.reset_index()
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
    **How to Use This Dashboard for Stock Analysis:**

    - **Company Info:** Understand what the business does, its size, and sector.
    - **Candlestick Charts:** Analyze price trends and market sentiment visually.
    - **Revenue & Income:** Evaluate how fast the company is growing and how profitable it is.
    - **Quarterly vs Annual:** Use quarterly to spot recent changes; use annual for long-term trends.
    - **Dividends:** See how the company returns profits to shareholders.
    - **Earnings Trends:** Compare earnings growth and revenue surprises.
    - **Balance Sheet:** Assess financial strength with asset and debt data.
    """)

    # Price History
    price_history = fetch_weekly_price_history(symbol)
    min_date, max_date = price_history['Date'].min(), price_history['Date'].max()
    start_date, end_date = st.date_input("Select date range for price chart:", (min_date, max_date), min_value=min_date, max_value=max_date)
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    filtered_price = price_history[(price_history['Date'] >= start_date) & (price_history['Date'] <= end_date)]

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
            buttons=list([
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
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
            revenue_chart = alt.Chart(df).mark_bar(color="#1f77b4").encode(
                x=alt.X(time_col, sort=None),
                y='Total Revenue'
            ).properties(height=300)
            st.altair_chart(revenue_chart, use_container_width=True)

    with income_col:
        st.subheader("Net Income")
        if 'Net Income' in df.columns:
            income_chart = alt.Chart(df).mark_bar(color="#ff7f0e").encode(
                x=alt.X(time_col, sort=None),
                y='Net Income'
            ).properties(height=300)
            st.altair_chart(income_chart, use_container_width=True)

    st.header('💸 Dividends')
    dividends = fetch_dividends(symbol)
    if not dividends.empty:
        min_div, max_div = dividends['Date'].min(), dividends['Date'].max()
        div_start, div_end = st.date_input("Select date range for dividends:", (min_div, max_div), min_value=min_div, max_value=max_div, key="div")
        div_start, div_end = pd.to_datetime(div_start), pd.to_datetime(div_end)
        filtered_div = dividends[(dividends['Date'] >= div_start) & (dividends['Date'] <= div_end)]
        dividend_chart = alt.Chart(filtered_div).mark_bar(color="#2ca02c").encode(
            x='Date:T',
            y='Dividends:Q'
        ).properties(height=300)
        st.altair_chart(dividend_chart, use_container_width=True)
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
        balance_chart = alt.Chart(balance_long).mark_line(point=True).encode(
            x='Date:T',
            y='value:Q',
            color='variable:N'
        ).properties(height=400)
        st.altair_chart(balance_chart, use_container_width=True)
    else:
        st.write("No balance sheet data available.")
