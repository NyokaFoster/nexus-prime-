from flask import Flask, render_template
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

markets = {
    "GOLD": "GC=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "BTC/USD": "BTC-USD",
    "ETH/USD": "ETH-USD",
    "DOGE/USD": "DOGE-USD",
    "SOL/USD": "SOL-USD"
}

@app.route("/")

def home():

    signals = []

    for market_name, ticker_symbol in markets.items():

        asset = yf.Ticker(ticker_symbol)

        data = asset.history(period="1mo", interval="5m")

        close_prices = data["Close"]

        delta = close_prices.diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))

        latest_rsi = rsi.iloc[-1]
        latest_price = close_prices.iloc[-1]

        short_ma = close_prices.rolling(window=5).mean()
        long_ma = close_prices.rolling(window=20).mean()

        latest_short = short_ma.iloc[-1]
        latest_long = long_ma.iloc[-1]

        confidence = 50

        trend_strength = abs(latest_short - latest_long)

        if trend_strength > 1:
            confidence += 10

        if trend_strength > 3:
            confidence += 10

        if latest_price > latest_short:
            confidence += 10

        if latest_price > latest_long:
            confidence += 10

        confidence = min(confidence, 99)
 
        if latest_short > latest_long and latest_rsi > 55:

            signal = "BUY"
            color = "green"

        elif latest_short < latest_long and latest_rsi < 45:

            signal = "SELL" 
            color = "red"
        else:

            signal = "WAIT"
            color = "gray"

        signal_data = {
            "market": market_name,
            "signal": signal,
            "color": color,
            "entry": round(latest_price, 5),
            "stop_loss": round(latest_price *0.995, 5),
            "take_profit": round(latest_price *1.01, 5),
            "confidence": confidence,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rsi" : round(latest_rsi, 2)
        }

        signals.append(signal_data)

    return render_template(
        "index.html",
        signals=signals
    )

if __name__ == "__main__":
    app.run(debug=True)