import streamlit as st
import yfinance as yf
import altair as alt
import plotly.graph_objects as go
import pandas as pd

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
    return yf.Ticker(symbol).history(period='1y', interval='1wk')

@st.cache_data
def fetch_dividends(symbol):
    return yf.Ticker(symbol).dividends

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
    st.markdown(f"**Name:** {information.get('longName', 'N/A')}  ")
    st.markdown(f"**Sector:** {information.get('sector', 'N/A')}  ")
    st.markdown(f"**Industry:** {information.get('industry', 'N/A')}  ")
    st.markdown(f"**Market Cap:** {information.get('marketCap', 0):,}  ")
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

    This dashboard helps both **short-term traders** and **long-term investors** make informed decisions
    based on fundamental and technical insights.
    """)

    price_history = fetch_weekly_price_history(symbol).rename_axis('Date').reset_index()

    st.header('📈 Price History & Candlestick Chart')
    candle_chart = go.Figure(data=[
        go.Candlestick(
            x=price_history['Date'],
            open=price_history['Open'],
            high=price_history['High'],
            low=price_history['Low'],
            close=price_history['Close'],
            increasing_line_color='green',
            decreasing_line_color='red'
        )
    ])
    candle_chart.update_layout(template="plotly_white", xaxis_rangeslider_visible=False)
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
        dividends = dividends.reset_index()
        dividend_chart = alt.Chart(dividends).mark_bar(color="#2ca02c").encode(
            x='Date:T',
            y='Dividends:Q'
        ).properties(height=300)
        st.altair_chart(dividend_chart, use_container_width=True)
    else:
        st.write("No dividend data available.")

    st.header('📉 Earnings Performance')
    earnings = fetch_earnings(symbol)
    if not earnings.empty:
        earnings = earnings.reset_index()
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
        balance = balance.reset_index().rename(columns={'index': 'Date'})
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
