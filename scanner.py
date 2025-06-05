import requests
import time
from telegram import Bot

# 🔐 Environment variables (set these in Render settings)
import os
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 📤 Send alert to Telegram
def send_telegram_alert(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")

# 📊 Fetch low float tickers (placeholder — replace with actual implementation)
def fetch_low_float_tickers():
    return ["HOLO", "STSS", "UAMY", "BTBT", "AYRO", "MCTR"]  # Add more as needed

# 🚨 Check for volume spikes
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

        url_live = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/2025-06-05/2025-06-05"
        current = requests.get(url_live).json()
        bars = current.get("results", [])
        if not bars:
            continue
        cur_vol = bars[0].get("v", 0)

        if cur_vol > 2 * avg_volume:
            message = f"<b>📈 Volume Spike Detected</b>\n"
            message += f"<b>Ticker:</b> {ticker}\n"
            message += f"<b>Current Vol:</b> {cur_vol}\n"
            message += f"<b>Avg Vol:</b> {avg_volume}\n"
            message += f"<b>Float:</b> <10M\n"
            message += f"<b>RelVol:</b> > 2.0"
            send_telegram_alert(message)
            time.sleep(1)

# 🔁 Scanner loop
def run_scanner():
    while True:
        try:
            tickers = fetch_low_float_tickers()
            check_volume_spikes(tickers)
        except Exception as e:
            print("Error:", e)
        time.sleep(60)

# 🏁 Entry point
if __name__ == "__main__":
    run_scanner()
python-telegram-bot==13.15
requests
