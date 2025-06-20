# 📊 Stock Market Analysis Dashboard

## 🧭 Introduction & Purpose

The **Stock Market Analysis Dashboard** is a dynamic and interactive web application built using **Streamlit** and **Yahoo Finance data**. It is designed for **both beginner and intermediate investors** to explore detailed insights into publicly traded companies — including price trends, key financial indicators, and fundamental ratios — in a simplified, visual format.

This tool is suitable for **educational use, portfolio tracking, and basic investment screening**, with built-in interpretation guides that make financial concepts approachable.

---

## 🔗 Live Dashboard

👉 [Launch the Dashboard](https://stock-market-app-9e2d5cb4qced4ea9hdbtud.streamlit.app/)

---

## 🚀 Functionality Overview

- ✅ View company fundamentals and trading currency
- ✅ Select any stock symbol and filter by time range
- ✅ Interactive candlestick chart with zoom slider
- ✅ 20-day and 50-day Moving Averages
- ✅ RSI (Relative Strength Index) and MFI (Money Flow Index)
- ✅ Visualized Total Revenue and Net Income (Quarterly or Annual)
- ✅ Dividend timeline and history
- ✅ Balance Sheet snapshots for the last 4 periods
- ✅ Financial ratios like PE, PB, ROE, Current Ratio, Debt-to-Equity
- ✅ Interpretation guides after each section

---

## 🛠️ Process Overview

| Section                  | Details |
|--------------------------|---------|
| **Libraries Used**       | `streamlit`, `yfinance`, `altair`, `plotly`, `pandas`, `numpy`, `datetime` |
| **Data Source**          | Yahoo Finance (via `yfinance`) |
| **Core Components**      | - `st.text_input()` for symbol entry<br>- `st.date_input()` for date filters<br>- `st.radio()` for toggling views |
| **Charts Implemented**   | - Candlestick chart (Plotly)<br>- MA, RSI, MFI (Plotly line charts)<br>- Revenue/Income (Altair bars)<br>- Balance sheet (Altair lines)<br>- Dividends (Altair bars) |
| **Key Ratios**           | PE, PB, Debt-to-Equity, ROE, Current Ratio |
| **Guides Added**         | Beginner-friendly explanations after each section to help interpret financial data |
| **Caching**              | Used `@st.cache_data` to optimize performance |
| **Code Structure**       | Modular fetch functions for data reuse and clarity |

---

## 🧩 Challenges Faced

| Challenge | Description |
|----------|-------------|
| **Date Parsing Errors** | Inconsistent `Date` formats in dividend and historical price data required careful normalization using `pd.to_datetime(..., errors='coerce')`. |
| **Streamlit Redacted Errors** | Errors like `TypeError` and `AttributeError` in Streamlit’s log required defensive programming (e.g., checking column existence before plotting). |
| **Empty or Delisted Data** | Some tickers lack dividend or balance sheet data; handled with conditional checks and default messages. |
| **Timezone Normalization** | Ensuring date inputs matched `UTC` format for proper filtering. |

---

## ⚠️ Limitations

- Depends on `yfinance`, which may have missing or outdated data for some tickers.
- Technical indicators use **weekly** data, which might be too coarse for intraday or short-term trading signals.
- No export or report generation feature.
- Limited error messaging when ticker data is invalid or API fails silently.
- RSI and MFI are calculated with default 14-period settings — no customization yet.

---

## 💼 Use Cases

- 🧑‍🎓 Educational tool for finance and investing courses  
- 📈 Entry-level stock research and screening  
- 📊 Comparative analysis of companies  
- 🧪 Prototype for a more robust trading assistant or equity dashboard

---

## 🌱 Future Improvements

- [ ] Add watchlist & favorite stocks
- [ ] Compare multiple symbols side-by-side
- [ ] Allow intraday & daily intervals with toggles
- [ ] Export as PDF or Excel report
- [ ] Add sentiment analysis or news headlines
- [ ] Allow users to toggle indicator parameters (e.g., RSI periods)

---
