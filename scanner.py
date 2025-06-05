import os
import time
import requests
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Failed to send Telegram message:", e)

def fetch_low_float_tickers():
    url = "https://api.polygon.io/v3/reference/tickers"
    params = {
        "market": "stocks",
        "active": "true",
        "limit": 1000,
        "apiKey": POLYGON_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    return [t['ticker'] for t in data.get("results", []) if t.get("share_class_shares_outstanding", 1e10) < 10_000_000]

def check_volume_spikes(tickers):
    for ticker in tickers:
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
        params = {
            "adjusted": "true",
            "apiKey": POLYGON_API_KEY
        }
        response = requests.get(url, params=params)
        results = response.json().get("results", [])
        if not results:
            continue
        avg_volume = results[0].get("v", 0)

        url_live = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{datetime.now().date()}/{datetime.now().date()}?adjusted=true&sort=desc&limit=1&apiKey={POLYGON_API_KEY}"
        current = requests.get(url_live).json()
        bars = current.get("results", [])
        if not bars:
            continue
        cur_vol = bars[0].get("v", 0)
        if cur_vol > 2 * avg_volume:
            message = f"<b>📊 Volume Spike Detected</b>
<b>Ticker:</b> {ticker}
<b>Current Vol:</b> {cur_vol:,}
<b>Avg Vol:</b> {avg_volume:,}
<b>Float:</b> <10M
<b>RelVol:</b> > 2.0"
            send_telegram_alert(message)
        time.sleep(1)

def run_scanner():
    while True:
        try:
            tickers = fetch_low_float_tickers()
            check_volume_spikes(tickers)
        except Exception as e:
            print("Error:", e)
        time.sleep(60)

if __name__ == "__main__":
    run_scanner()
