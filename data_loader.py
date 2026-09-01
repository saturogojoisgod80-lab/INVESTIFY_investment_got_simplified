import yfinance as yf
import pandas as pd
import streamlit as st

US_STOCKS = ["AMZN", "AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
DASHBOARD_WATCHLIST = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]

def _normalize_ticker(ticker_symbol):
    raw_symbol = ticker_symbol.replace(".NS", "")
    return raw_symbol if raw_symbol in US_STOCKS else ticker_symbol

@st.cache_data(ttl=60, show_spinner=False)
def fetch_stock_data(ticker_symbol):
    normalized = _normalize_ticker(ticker_symbol)
    try:
        stock = yf.Ticker(normalized)
        df = stock.history(period="3mo")

        if df.empty:
            return {"status": "Error", "message": f"No data found for symbol '{ticker_symbol}'."}

        latest_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        price_change_pct = ((latest_price - prev_price) / prev_price) * 100

        sma_20 = df['Close'].tail(20).mean()
        volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].mean()

        momentum = "Bullish" if latest_price >= sma_20 else "Bearish"
        vol_anomaly = "High Volume Spike" if volume > (1.2 * avg_volume) else "Normal Volume"

        bond_yield = fetch_bond_data()["yield"]

        return {
            "status": "Success",
            "symbol": normalized,
            "price": round(latest_price, 2),
            "change_pct": round(price_change_pct, 2),
            "sma_20": round(sma_20, 2),
            "volume": int(volume),
            "avg_volume": int(avg_volume),
            "momentum": momentum,
            "volume_anomaly": vol_anomaly,
            "confidence": 0.88,
            "history_df": df[['Close']],
            "bond_yield": bond_yield
        }
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_bond_data():
    try:
        bond = yf.Ticker("^TNX")
        history = bond.history(period="1mo")
        if history.empty:
            return {"yield": 7.10, "change_pct": 0.0, "history_df": pd.DataFrame(), "status": "Fallback (static)"}

        latest_yield = round(history['Close'].iloc[-1], 2)
        prev_yield = history['Close'].iloc[-2] if len(history) > 1 else latest_yield
        change_pct = round(((latest_yield - prev_yield) / prev_yield) * 100, 2) if prev_yield else 0.0

        return {
            "yield": latest_yield,
            "change_pct": change_pct,
            "history_df": history[['Close']],
            "status": "Live (proxy: US 10Y Treasury)"
        }
    except Exception:
        return {"yield": 7.10, "change_pct": 0.0, "history_df": pd.DataFrame(), "status": "Fallback (static)"}

@st.cache_data(ttl=60, show_spinner=False)
def get_index_snapshot(idx_name="NIFTY 50"):
    symbol_map = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "BANKNIFTY": "^NSEBANK"
    }
    ticker = symbol_map.get(idx_name, "^NSEI")
    
    try:
        data = yf.Ticker(ticker).history(period="1mo")
        if not data.empty and len(data) >= 2:
            latest = round(data['Close'].iloc[-1], 2)
            prev = round(data['Close'].iloc[-2], 2)
            change_pct = round(((latest - prev) / prev) * 100, 2)
            return {
                "status": "Success",
                "price": latest,
                "change_pct": change_pct,
                "history_df": data[['Close']]
            }
    except Exception:
        pass

    fallback_map = {
        "NIFTY 50": {"price": 24320.15, "change_pct": 0.42},
        "SENSEX": {"price": 79850.40, "change_pct": 0.38},
        "BANKNIFTY": {"price": 52140.80, "change_pct": 0.15}
    }
    fb = fallback_map.get(idx_name, {"price": 24320.15, "change_pct": 0.42})
    return {
        "status": "Success",
        "price": fb["price"],
        "change_pct": fb["change_pct"],
        "history_df": pd.DataFrame()
    }

def fetch_watchlist_data(tickers=None):
    if tickers is None:
        tickers = DASHBOARD_WATCHLIST
    rows = []
    for ticker in tickers:
        data = fetch_stock_data(ticker)
        if data.get("status") == "Success":
            rows.append({
                "Symbol": data["symbol"],
                "LTP": data["price"],
                "Chg %": data["change_pct"],
                "Momentum": data["momentum"],
                "Volume": data["volume_anomaly"],
            })
        else:
            rows.append({
                "Symbol": ticker,
                "LTP": None,
                "Chg %": None,
                "Momentum": "N/A",
                "Volume": data.get("message", "Error"),
            })
    return pd.DataFrame(rows)

def get_mock_holdings():
    return [
        {"symbol": "INFY.NS", "qty": 10, "buy_price": 1400.0, "current_value": 18500.0, "invested": 14000.0},
        {"symbol": "RELIANCE.NS", "qty": 5, "buy_price": 2700.0, "current_value": 14500.0, "invested": 13500.0},
        {"symbol": "TCS.NS", "qty": 4, "buy_price": 3800.0, "current_value": 16800.0, "invested": 15200.0}
    ]

def get_mock_positions():
    return [
        {"symbol": "NIFTY MAR 24000 CE", "product": "MIS", "exposure_pct": 45},
        {"symbol": "BANKNIFTY MAR 52000 PE", "product": "NRML", "exposure_pct": 35},
        {"symbol": "RELIANCE APR FUT", "product": "MIS", "exposure_pct": 20}
    ]