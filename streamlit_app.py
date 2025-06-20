import streamlit as st
import yfinance as yf
import altair as alt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import io

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
    return {
        "PE Ratio": info.get("trailingPE"),
        "PB Ratio": info.get("priceToBook"),
        "Debt to Equity": info.get("debtToEquity"),
        "Return on Equity": info.get("returnOnEquity"),
        "Current Ratio": info.get("currentRatio"),
    }

# --- PAGE ROUTER ---
page = st.sidebar.selectbox("Choose a Page", ["📊 Single Stock Analysis", "📈 Compare Multiple Stocks"])

# --- SINGLE STOCK ANALYSIS PAGE ---
if page == "📊 Single Stock Analysis":
    symbol = st.text_input('Enter a stock symbol:', 'AAPL')
    rsi_period = st.sidebar.slider("RSI Period", min_value=7, max_value=30, value=14, step=1)

    if symbol:
        ticker = yf.Ticker(symbol)
        info = fetch_stock_info(symbol)

        st.header('🏢 Company Information')
        st.markdown(f"**Name:** {info.get('longName', 'N/A')}")
        st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
        st.markdown(f"**Currency:** {info.get('currency', 'N/A')}")
        st.markdown(f"**Market Cap:** {info.get('marketCap', 0):,}")

        st.subheader("📌 Guide: Company Info")
        st.markdown("""This section outlines the basic identity and economic size of the company.""")

        price = fetch_weekly_price_history(symbol)
        price['MA20'] = price['Close'].rolling(window=20).mean()
        price['MA50'] = price['Close'].rolling(window=50).mean()

        delta = price['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(rsi_period).mean()
        loss = -delta.where(delta < 0, 0).rolling(rsi_period).mean()
        rs = gain / loss
        price['RSI'] = 100 - (100 / (1 + rs))

        typical_price = (price['High'] + price['Low'] + price['Close']) / 3
        money_flow = typical_price * price['Volume']
        pos_flow = money_flow.where(delta > 0, 0).rolling(rsi_period).sum()
        neg_flow = money_flow.where(delta < 0, 0).rolling(rsi_period).sum()
        price['MFI'] = 100 * (pos_flow / (pos_flow + neg_flow))

        st.subheader("📉 Indicators")
        st.line_chart(price.set_index('Date')[['Close', 'MA20', 'MA50']])
        st.line_chart(price.set_index('Date')[['RSI']])
        st.line_chart(price.set_index('Date')[['MFI']])

        st.subheader("📄 Export Data")
        export_btn = st.radio("Select export format:", ["None", "Excel"])
        if export_btn == "Excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                price.to_excel(writer, index=False, sheet_name="Indicators")
            st.download_button("Download Excel Report", output.getvalue(), file_name=f"{symbol}_analysis.xlsx")

# --- COMPARE MULTIPLE STOCKS PAGE ---
elif page == "📈 Compare Multiple Stocks":
    symbols = st.text_input("Enter symbols separated by commas:", "AAPL,MSFT,GOOGL")
    if symbols:
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        df_list = []
        for sym in symbol_list:
            try:
                info = fetch_stock_info(sym)
                ratios = fetch_key_ratios(sym)
                row = {"Symbol": sym, "Name": info.get("shortName", sym)}
                row.update(ratios)
                df_list.append(row)
            except:
                continue
        if df_list:
            compare_df = pd.DataFrame(df_list)
            st.dataframe(compare_df.set_index("Symbol"))

