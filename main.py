import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Trading + Congress Trades", layout="wide")

# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------

@st.cache_data(ttl=60 * 30, show_spinner=False)
def get_price_history(ticker: str, period: str = "9mo") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()


def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def analyze_ticker(ticker: str) -> dict:
    """Rule-based scoring. Every point added/subtracted has a stated reason."""
    df = get_price_history(ticker)
    if df.empty or len(df) < 60:
        return {"ticker": ticker, "error": "Not enough price history returned."}

    close = df["Close"]
    volume = df["Volume"]

    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    rsi = compute_rsi(close)
    macd_line, signal_line, hist = compute_macd(close)
    vol_avg20 = volume.rolling(20).mean()

    last_close = close.iloc[-1]
    last_sma20 = sma20.iloc[-1]
    last_sma50 = sma50.iloc[-1]
    last_rsi = rsi.iloc[-1]
    last_macd_hist = hist.iloc[-1]
    prev_macd_hist = hist.iloc[-2]
    last_vol = volume.iloc[-1]
    last_vol_avg = vol_avg20.iloc[-1]

    pct_change_1m = (last_close / close.iloc[-21] - 1) * 100 if len(close) > 21 else np.nan

    score = 0
    reasons = []

    # Trend: price vs moving averages
    if last_close > last_sma20 > last_sma50:
        score += 2
        reasons.append("Price is above both the 20-day and 50-day moving averages, and the 20-day is above the 50-day (uptrend structure).")
    elif last_close < last_sma20 < last_sma50:
        score -= 2
        reasons.append("Price is below both moving averages, and the 20-day is below the 50-day (downtrend structure).")
    elif last_close > last_sma50:
        score += 1
        reasons.append("Price is above the 50-day moving average (longer-term trend leaning up).")
    else:
        score -= 1
        reasons.append("Price is below the 50-day moving average (longer-term trend leaning down).")

    # Momentum: RSI
    if last_rsi < 30:
        score += 1
        reasons.append(f"RSI is {last_rsi:.1f}, in oversold territory (<30) — potential mean-reversion setup.")
    elif last_rsi > 70:
        score -= 1
        reasons.append(f"RSI is {last_rsi:.1f}, in overbought territory (>70) — extended, higher pullback risk.")
    else:
        reasons.append(f"RSI is {last_rsi:.1f}, a neutral reading.")

    # MACD histogram turning
    if last_macd_hist > 0 and prev_macd_hist <= 0:
        score += 2
        reasons.append("MACD histogram just crossed positive — a fresh bullish momentum signal.")
    elif last_macd_hist < 0 and prev_macd_hist >= 0:
        score -= 2
        reasons.append("MACD histogram just crossed negative — a fresh bearish momentum signal.")
    elif last_macd_hist > 0:
        score += 1
        reasons.append("MACD histogram is positive — momentum currently favors buyers.")
    else:
        score -= 1
        reasons.append("MACD histogram is negative — momentum currently favors sellers.")

    # Volume confirmation
    if last_vol > 1.5 * last_vol_avg and last_close > close.iloc[-2]:
        score += 1
        reasons.append("Today's volume is well above the 20-day average on an up day — buying interest confirmation.")
    elif last_vol > 1.5 * last_vol_avg and last_close < close.iloc[-2]:
        score -= 1
        reasons.append("Today's volume is well above the 20-day average on a down day — selling pressure confirmation.")

    if score >= 3:
        verdict = "BUY (bullish signal)"
    elif score <= -3:
        verdict = "SELL / AVOID (bearish signal)"
    else:
        verdict = "HOLD / NEUTRAL"

    return {
        "ticker": ticker,
        "last_close": round(float(last_close), 2),
        "pct_change_1m": round(float(pct_change_1m), 2) if not np.isnan(pct_change_1m) else None,
        "rsi": round(float(last_rsi), 1),
        "score": score,
        "verdict": verdict,
        "reasons": reasons,
    }


# --------------------------------------------------------------------------
# Congress trading helpers (QuiverQuant)
# --------------------------------------------------------------------------

QUIVER_BASE = "https://api.quiverquant.com"


@st.cache_data(ttl=60 * 30, show_spinner=False)
def get_congress_trades(api_key: str, ticker: str | None = None) -> pd.DataFrame:
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    if ticker:
        url = f"{QUIVER_BASE}/beta/historical/congresstrading/{ticker.upper()}"
    else:
        url = f"{QUIVER_BASE}/beta/bulk/congresstrading"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    df = pd.DataFrame(data)
    return df


# --------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------

st.title("📈 AI Trading Strategy & Congress Trades")

tab1, tab2 = st.tabs(["🤖 AI Trading Strategy", "🏛️ Congress Trades"])

# ---- Tab 1 ----
with tab1:
    st.subheader("Rule-based technical screener")
    st.caption(
        "This scores tickers using transparent technical rules (trend, RSI, MACD, volume). "
        "It is **not** financial advice — it's a decision-support tool. Verify independently."
    )

    default_tickers = "AAPL, MSFT, NVDA, TSLA, AMZN"
    tickers_input = st.text_input("Tickers to analyze (comma-separated)", value=default_tickers)
    run = st.button("Run Analysis", type="primary")

    if run:
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        results = []
        with st.spinner("Fetching data and computing signals..."):
            for t in tickers:
                try:
                    results.append(analyze_ticker(t))
                except Exception as e:
                    results.append({"ticker": t, "error": str(e)})

        summary_rows = []
        for r in results:
            if "error" in r:
                summary_rows.append({"Ticker": r["ticker"], "Verdict": "ERROR", "Score": None,
                                      "Last Close": None, "1M % Chg": None, "RSI": None})
            else:
                summary_rows.append({
                    "Ticker": r["ticker"],
                    "Verdict": r["verdict"],
                    "Score": r["score"],
                    "Last Close": r["last_close"],
                    "1M % Chg": r["pct_change_1m"],
                    "RSI": r["rsi"],
                })
        summary_df = pd.DataFrame(summary_rows).sort_values("Score", ascending=False, na_position="last")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.markdown("### Detailed reasoning")
        for r in results:
            if "error" in r:
                st.error(f"**{r['ticker']}**: {r['error']}")
                continue
            with st.expander(f"{r['ticker']} — {r['verdict']} (score: {r['score']})"):
                for reason in r["reasons"]:
                    st.markdown(f"- {reason}")

        st.info(
            
        )
    else:
        st.info("Enter tickers and click **Run Analysis** to generate signals.")

# ---- Tab 2 ----
with tab2:
    st.subheader("US Congress Stock Trading Disclosures")
    st.caption("Data source: QuiverQuant API. Requires your own API key.")

    api_key = st.text_input("QuiverQuant API Key", type="password",
                             help="Get a key at quiverquant.com. Not stored anywhere — used only for this session.")
    filter_ticker = st.text_input("Filter by ticker (optional, e.g. NVDA)", value="")

    fetch = st.button("Fetch Congress Trades", type="primary")

    if fetch:
        if not api_key:
            st.warning("Enter your QuiverQuant API key first.")
        else:
            try:
                with st.spinner("Fetching congressional trading data..."):
                    df = get_congress_trades(api_key, filter_ticker.strip() or None)
                if df.empty:
                    st.warning("No data returned. Check your ticker/API key.")
                else:
                    date_col = next((c for c in ["TransactionDate", "Traded", "Date"] if c in df.columns), None)
                    if date_col:
                        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                        df = df.sort_values(date_col, ascending=False)

                    st.dataframe(df, use_container_width=True, hide_index=True)

                    if "Transaction" in df.columns and "Ticker" in df.columns:
                        st.markdown("### Most active tickers (by disclosure count)")
                        top_tickers = df["Ticker"].value_counts().head(10)
                        st.bar_chart(top_tickers)
            except requests.exceptions.HTTPError as e:
                st.error(f"API error: {e}. Check that your API key is valid and has access to this endpoint.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
    else:
        st.info("Enter your API key and click **Fetch Congress Trades**.")

st.markdown("---")
st.caption(
    "Disclaimer: This application is provided for educational and informational purposes only "
    "and does not constitute financial, investment, or trading advice."
)
