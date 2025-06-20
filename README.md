# 📊 Stock Market Analysis Dashboard

A visually rich and interactive web application built using **Streamlit**, designed to help users analyze company stocks using fundamental financial indicators, charts, and interpretation guides.

---

## 🔗 Live Dashboard

🌐 [Launch the App](https://stock-market-app-9e2d5cb4qced4ea9hdbtud.streamlit.app/)  

---

## 🎯 Purpose

This dashboard aims to:
- Simplify stock market analysis for retail investors and students.
- Offer interactive charts and key financial data in a beginner-friendly format.
- Educate users through interpretation guides that explain ratios and signals.
- Allow quick comparisons of financial health between companies.

---

## 🛠️ Features & Functionality

- 🔍 **Company Info:** Name, Sector, Industry, Market Cap, and Website.
- 📈 **Candlestick Chart:** Visualizes weekly stock prices with zoom support.
- 📉 **Moving Averages:** Displays MA20 and MA50 trend lines.
- 📊 **RSI & MFI Charts:** Shows momentum and volume-based trend strength.
- 💸 **Dividends Visualization:** View dividend history with date filtering.
- 📐 **Key Ratios:** PE, PB, ROE, Debt-to-Equity, and Current Ratio.
- 📊 **Financial Performance:** Revenue and Net Income bar charts.
- 📊 **Peer Comparison:** Compare multiple stocks side by side.
- 📘 **Interpretation Guides:** Every major section is accompanied by an educational guide.

---

## 🔄 Process Overview

| Area                     | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| **Libraries Used**       | `streamlit`, `yfinance`, `pandas`, `numpy`, `altair`, `plotly.graph_objects` |
| **Caching**              | Used `@st.cache_data` to optimize API calls and avoid repeated data fetches.|
| **Charts**               | Plotly (candlesticks, MAs), Altair (bars), Streamlit (line charts)         |
| **Date Handling**        | `datetime`, `pd.to_datetime()`, `.tz_localize(None)` for consistent filtering |
| **Data Sources**         | Fetched directly from **Yahoo Finance** using `yfinance`                   |
| **Financial Ratios**     | Extracted from `yf.Ticker().info` and calculated/displayed dynamically     |
| **Dividends**            | Filtered over last 10 years, interactive date slider, and visualized       |
| **Guides**               | Markdown-based interpretation guides after every major visual section      |
| **Multiple Symbol Input**| Input comma-separated tickers and compare them in a unified table          |

---

## ⚠️ Challenges Faced

| Issue | Explanation |
|-------|-------------|
| **Timezone Errors** | Dividend dates returned in timezone-aware formats (`America/New_York`) caused comparison errors with naive datetimes. Fixed using `.dt.tz_localize(None)`. |
| **Empty DataFrames** | Several cases where dividend or historical price data was missing or returned empty, causing chart or date slider errors. Resolved with `if not df.empty` checks. |
| **Type Mismatch** | In some cases, improper tuple unpacking or malformed `st.date_input` default values caused syntax or runtime errors. Fixed with corrected function signatures. |
| **Missing Ratios** | When certain financial keys were missing from `yfinance`, default values like `info.get("key")` returned `None`. Handled gracefully without crashing the app. |

---

## 🚧 Limitations

- Relies solely on **Yahoo Finance** data which may be incomplete or delayed.
- No technical indicators beyond RSI and MFI (e.g., MACD, Bollinger Bands).
- Focuses on **weekly** price trends — lacks intraday or daily resolution.
- No backend/database for saving user preferences or watchlists.

---

## ✅ Use Cases

- 📚 **Finance Education**: Students learning investment analysis.
- 📈 **Stock Research**: Investors comparing fundamentals and trends.
- 🧪 **Prototype Demos**: Startup ideas around fintech dashboards.
- 🧑‍🏫 **Teaching Aid**: Professors or tutors introducing market tools.

---

## 🚀 Future Improvements

- Add **EPS, dividend yield, and payout ratio** stats.
- Include **technical indicators** (e.g., MACD, Bollinger Bands).
- Add **real-time news and sentiment analysis** integration.
- Enable **portfolio simulation** or user-based bookmarking.

