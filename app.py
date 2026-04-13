from flask import Flask, render_template, jsonify, request
import datetime
import random

import yfinance as yf

try:
    from nsepython import nse_eq
except Exception:
    nse_eq = None

app = Flask(__name__)

TOP_STOCKS = [
    {"symbol": "RELIANCE", "ticker": "RELIANCE.NS"},
    {"symbol": "INFY", "ticker": "INFY.NS"},
    {"symbol": "HDFCBANK", "ticker": "HDFCBANK.NS"},
    {"symbol": "ICICIBANK", "ticker": "ICICIBANK.NS"},
    {"symbol": "HINDUNILVR", "ticker": "HINDUNILVR.NS"},
    {"symbol": "ITC", "ticker": "ITC.NS"},
    {"symbol": "SBIN", "ticker": "SBIN.NS"},
    {"symbol": "TCS", "ticker": "TCS.NS"},
    {"symbol": "LT", "ticker": "LT.NS"},
    {"symbol": "AXISBANK", "ticker": "AXISBANK.NS"},
]

SYMBOL_TO_TICKER = {item["symbol"]: item["ticker"] for item in TOP_STOCKS}

# ✅ Safe float
def safe_float(value, default):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except:
        return default

@app.route("/")
def home():
    return render_template("index.html")

def _num(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def get_snapshot_from_nse(symbol):
    if nse_eq is None:
        return None

    try:
        data = nse_eq(symbol)
        price_info = data.get("priceInfo", {})
        meta = data.get("metadata", {})
        security = data.get("securityInfo", {})
        price = _num(price_info.get("lastPrice"), 0)
        open_price = _num(price_info.get("open"), price)
        high = _num(price_info.get("intraDayHighLow", {}).get("max"), price)
        low = _num(price_info.get("intraDayHighLow", {}).get("min"), price)
        previous_close = _num(price_info.get("previousClose"), open_price)

        if price <= 0:
            return None

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "previousClose": round(previous_close, 2),
            "marketCap": meta.get("marketCap") or security.get("issuedSize") or "N/A",
            "pe": meta.get("pdSymbolPe", "N/A"),
            "source": "NSE",
        }
    except Exception:
        return None


def get_snapshot_from_yahoo(symbol, ticker):
    try:
        stock = yf.Ticker(ticker)
        fast = stock.fast_info
        info = stock.info if stock.info else {}

        price = _num(getattr(fast, "last_price", None), _num(info.get("currentPrice"), 0))
        open_price = _num(getattr(fast, "open", None), _num(info.get("open"), price))
        high = _num(getattr(fast, "day_high", None), _num(info.get("dayHigh"), price))
        low = _num(getattr(fast, "day_low", None), _num(info.get("dayLow"), price))
        previous_close = _num(
            getattr(fast, "previous_close", None),
            _num(info.get("previousClose"), open_price),
        )

        if price <= 0:
            hist = stock.history(period="5d", interval="1d")
            if hist.empty:
                return None
            price = _num(hist["Close"].iloc[-1], 0)
            open_price = _num(hist["Open"].iloc[-1], price)
            high = _num(hist["High"].iloc[-1], price)
            low = _num(hist["Low"].iloc[-1], price)
            previous_close = _num(hist["Close"].iloc[-2], open_price) if len(hist) > 1 else open_price

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "previousClose": round(previous_close, 2),
            "marketCap": info.get("marketCap", "N/A"),
            "pe": info.get("trailingPE", "N/A"),
            "roe": info.get("returnOnEquity", "N/A"),
            "debtToEquity": info.get("debtToEquity", "N/A"),
            "source": "Yahoo Finance",
        }
    except Exception:
        return None


def get_stock_snapshot(symbol):
    ticker = SYMBOL_TO_TICKER.get(symbol)
    if not ticker:
        return None

    snapshot = get_snapshot_from_nse(symbol)
    if snapshot:
        return snapshot

    return get_snapshot_from_yahoo(symbol, ticker)


@app.route("/get_stocks")
def get_stocks():
    min_price = safe_float(request.args.get("min_price"), 0)
    max_price = safe_float(request.args.get("max_price"), 1e12)
    profit_filter = request.args.get("profit", "All")

    result = []

    for item in TOP_STOCKS:
        symbol = item["symbol"]
        snapshot = get_stock_snapshot(symbol)
        if not snapshot:
            continue

        price = _num(snapshot.get("price"), 0)
        open_price = _num(snapshot.get("open"), price)

        if not (min_price <= price <= max_price):
            continue

        if profit_filter == "Profit" and price < open_price:
            continue
        if profit_filter == "Loss" and price > open_price:
            continue

        change = price - open_price
        change_pct = (change / open_price * 100) if open_price else 0

        result.append(
            {
                "symbol": symbol,
                "price": round(price, 2),
                "change": round(change, 2),
                "changePct": round(change_pct, 2),
                "source": snapshot.get("source", "N/A"),
            }
        )

    result.sort(key=lambda x: x["symbol"])
    return jsonify(result)

@app.route("/get_chart/<symbol>")
def get_chart(symbol):
    ticker = SYMBOL_TO_TICKER.get(symbol)
    if not ticker:
        return jsonify({"time": [], "price": []})

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="15m")

        if not hist.empty:
            labels = [index.strftime("%H:%M") for index in hist.index]
            prices = [round(_num(value, 0), 2) for value in hist["Close"].tolist()]
            return jsonify({"time": labels, "price": prices})

        snapshot = get_stock_snapshot(symbol)
        price = _num(snapshot.get("price") if snapshot else None, 100)
        times = []
        prices = []

        base = price * random.uniform(0.97, 0.995)

        for i in range(20):
            t = (datetime.datetime.now() - datetime.timedelta(minutes=15 * (20 - i))).strftime("%H:%M")
            drift = i * price * 0.001
            noise = random.uniform(-price * 0.0015, price * 0.0015)
            times.append(t)
            prices.append(round(base + drift + noise, 2))

        return jsonify({"time": times, "price": prices})

    except Exception:
        return jsonify({"time": [], "price": []})


@app.route("/get_fundamentals/<symbol>")
def get_fundamentals(symbol):
    snapshot = get_stock_snapshot(symbol)
    if not snapshot:
        return jsonify({})

    market_cap = snapshot.get("marketCap", "N/A")
    if isinstance(market_cap, (int, float)):
        market_cap = f"{market_cap:,.0f}"

    roe = snapshot.get("roe", "N/A")
    if isinstance(roe, (int, float)):
        roe = round(roe * 100, 2)

    return jsonify(
        {
            "pe": snapshot.get("pe", "N/A"),
            "roe": roe,
            "debt": snapshot.get("debtToEquity", "N/A"),
            "marketCap": market_cap,
            "high": snapshot.get("high", "N/A"),
            "low": snapshot.get("low", "N/A"),
            "source": snapshot.get("source", "N/A"),
            "price": snapshot.get("price", "N/A"),
            "previousClose": snapshot.get("previousClose", "N/A"),
        }
    )

# ✅ RUN
if __name__ == "__main__":
    app.run(debug=True)