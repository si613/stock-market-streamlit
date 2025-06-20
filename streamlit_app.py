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

    st.header('📈 Candlestick Chart')
    fig_candle = go.Figure()
    fig_candle.add_trace(go.Candlestick(
        x=price['Date'], open=price['Open'], high=price['High'], low=price['Low'], close=price['Close'],
        increasing_line_color='green', decreasing_line_color='red', name='Candlestick'))
    fig_candle.update_layout(template="plotly_white", height=600, xaxis_rangeslider_visible=True)
    st.plotly_chart(fig_candle, use_container_width=True)

    st.subheader("📘 Interpretation Guide")
    st.markdown("""
    - **Candlestick Chart** shows price movement within each period (week).
    - A **green candle** means the stock closed higher than it opened — a bullish signal.
    - A **red candle** means the stock closed lower than it opened — a bearish signal.
    - The **wicks** show the high and low prices during that week.
    
    
    ---
    """)

    st.header('📉 Moving Averages')
    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(x=price['Date'], y=price['Close'], mode='lines', name='Close Price', line=dict(color='#999999')))
    fig_ma.add_trace(go.Scatter(x=price['Date'], y=price['MA20'], mode='lines', name='MA20', line=dict(color='#1f77b4')))
    fig_ma.add_trace(go.Scatter(x=price['Date'], y=price['MA50'], mode='lines', name='MA50', line=dict(color='#ff7f0e')))
    fig_ma.update_layout(template="plotly_white", height=500)
    st.plotly_chart(fig_ma, use_container_width=True)

    st.subheader("📘 Interpretation Guide")
    st.markdown("""
    - **Moving Averages (MA)** smooth out short-term price fluctuations.
    - **MA20** reflects the short-term trend (approx 1 month if weekly data).
    - **MA50** reflects the medium-term trend (approx 2.5 months).
    - When the short-term MA crosses above the long-term MA, it’s a bullish signal (called a **Golden Cross**).
    - When it crosses below, it’s bearish (called a **Death Cross**).
   
    
    ---
    """)

    st.header('📉 RSI Chart')
    st.line_chart(price.set_index('Date')[['RSI']])
    st.subheader("📘 Interpretation Guide")
    st.markdown("""
    - **RSI (Relative Strength Index)** is a momentum indicator.
    - It ranges from 0 to 100.
    - **RSI below 30** suggests the stock may be **oversold** (undervalued).
    - **RSI above 70** suggests the stock may be **overbought** (overvalued).
    - Traders use RSI to identify potential trend reversals.
    """)

    st.header('📉 MFI Chart')
    st.line_chart(price.set_index('Date')[['MFI']])
    st.subheader("📘 Interpretation Guide")
    st.markdown("""
    - **MFI (Money Flow Index)** uses both price and volume.
    - Also ranges from 0 to 100.
    - **MFI below 20** may indicate oversold, **above 80** may indicate overbought.
    - MFI is helpful for validating RSI signals with volume confirmation.
    
    
    ---
    """)

    
    st.header('📊 Financial Performance')
    view = st.radio("Select View:", ["Quarterly", "Annual"], horizontal=True)
    if view == 'Quarterly':
        fin = fetch_quarterly_financials(symbol).rename_axis('Quarter').reset_index()
        fin = fin.tail(5)
        bar_size = 50
    else:
        fin = fetch_annual_financials(symbol).rename_axis('Year').reset_index()
        fin[fin.columns[0]] = fin[fin.columns[0]].astype(str).str[:4]
        bar_size = 50

    time_col = fin.columns[0]
    cols = st.columns(2)
    with cols[0]:
        st.subheader("Total Revenue")
        if 'Total Revenue' in fin.columns:
            st.altair_chart(alt.Chart(fin).mark_bar(size=bar_size, color="#1f77b4").encode(x=alt.X(time_col, sort=None), y='Total Revenue').properties(height=300), use_container_width=True)
    with cols[1]:
        st.subheader("Net Income")
        if 'Net Income' in fin.columns:
            st.altair_chart(alt.Chart(fin).mark_bar(size=bar_size, color="#ff7f0e").encode(x=alt.X(time_col, sort=None),y='Net Income').properties(height=300), use_container_width=True)


    st.subheader("📘 Interpretation Guide")
    st.markdown("""Track how revenue and income evolve. Declines may signal trouble; growth shows strength.
    
    ---
    """)

st.header('💸 Dividends')
div = fetch_dividends(symbol)

if not div.empty:
    try:
        # Ensure 'Date' is parsed and timezone-naive
        div['Date'] = pd.to_datetime(div['Date'], errors='coerce')
        div['Date'] = div['Date'].dt.tz_localize(None)  # <-- remove timezone

        div = div.dropna(subset=['Date'])
        ten_years_ago = datetime.now() - pd.DateOffset(years=10)  # also timezone-naive

        div = div[div['Date'] >= ten_years_ago]

        if not div.empty:
            div_min, div_max = div['Date'].min(), div['Date'].max()

            div_range = st.date_input(
                "Select dividend date range:",
                value=(div_min.date(), div_max.date()),
                min_value=div_min.date(),
                max_value=div_max.date(),
                key="div"
            )

            if isinstance(div_range, tuple) and len(div_range) == 2:
                start = pd.to_datetime(div_range[0])
                end = pd.to_datetime(div_range[1])
                div = div[(div['Date'] >= start) & (div['Date'] <= end)]

            if not div.empty:
                st.altair_chart(
                    alt.Chart(div).mark_bar(color="#2ca02c")
                    .encode(x='Date:T', y='Dividends:Q')
                    .properties(height=300),
                    use_container_width=True
                )
            else:
                st.write("No dividends in selected range.")
        else:
            st.write("No dividends in the last 10 years.")
    except Exception as e:
        st.error(f"Error processing dividends: {e}")
else:
    st.write("No dividend data available.")

st.subheader("📘 Interpretation Guide")
st.markdown("""
Dividends reward shareholders. Consistent or growing dividends reflect financial health and shareholder commitment.


---
""")


# Display financial ratios for the main stock
st.header('📊 Key Financial Ratios')
st.markdown(f"### 📌 Financial Ratios for: `{symbol.upper()}`")
ratios = fetch_key_ratios(symbol)
styled_ratios = (
    pd.DataFrame(ratios.items(), columns=['Metric', 'Value'])
    .style
    .set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'left'), ('padding', '4px 8px')]},
        {'selector': 'td', 'props': [('text-align', 'left'), ('padding', '4px 8px')]}
    ])
    .set_properties(**{'width': '120px', 'text-align': 'left'})
)

st.dataframe(styled_ratios)

# Input and comparison for multiple companies
st.markdown("### 📌 Comparison Across Multiple Companies")
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

    
    st.markdown("""
    ### 📘 Interpretation Guide: Key Financial Ratios
    
    These ratios help assess a company's **valuation**, **profitability**, and **financial strength**.
    
    ##### 🔹 **PE Ratio (Price-to-Earnings)**
    - Shows how much investors pay for ₹1 of earnings. 
    - **Lower PE** → May indicate **undervaluation**. **Higher PE** → Market expects growth or the stock may be **overvalued**.
    
    ##### 🔹 **PB Ratio (Price-to-Book)**
    - Compares market price to the company's net asset value.
    - **PB < 1** → Possibly **undervalued**. **PB > 3** → May suggest **growth potential** or **overvaluation**.
    
    ##### 🔹 **ROE (Return on Equity)**
    - Measures how efficiently a company uses shareholder funds.
    - **ROE > 15%** → Indicates strong **profitability**.
    -**Low/Negative ROE** → Signals inefficiency or **losses**.
    
    ##### 🔹 **Debt-to-Equity Ratio**
    - Compares company debt to shareholder equity.
    - **< 1** → Company is using **less leverage** (financially safer).
    - **> 2** → Heavily reliant on **debt**, potentially risky.
    
    ##### 🔹 **Current Ratio**
    - Indicates ability to pay short-term obligations.
    - **> 1** → Good **liquidity**.
    - **< 1** → May struggle to cover short-term liabilities.
    
    ---
    """, unsafe_allow_html=True)

