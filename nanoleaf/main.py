import time
import requests
import yfinance as yf
from datetime import datetime
import pytz
import os
import logging
from logging.handlers import TimedRotatingFileHandler

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nanoleaf.log")
handler = TimedRotatingFileHandler(LOG_FILE, when="D", interval=1, backupCount=7)
handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %I:%M %p ET"))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

def log(msg):
    print(msg)
    logging.info(msg)

DEVICES = [
    {"name": "Lines",  "ip": "192.168.1.134", "token": "mI84OYhxVmeu2FiY1uvReRHkRB8mHPyx"},
    {"name": "Shapes", "ip": "192.168.1.54",  "token": "WjFNij5CtmHJiQOug0uwknxwxVDxSfrP"},
]

RED   = {"hue": 0,   "sat": 100, "brightness": 100}
GREEN = {"hue": 120, "sat": 100, "brightness": 100}

MARKET_OPEN  = (9, 30)
MARKET_CLOSE = (16, 0)
ET = pytz.timezone("America/New_York")
CHECK_INTERVAL = 5 * 60  # 5 minutes


def is_market_open():
    now = datetime.now(ET)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    t = (now.hour, now.minute)
    return MARKET_OPEN <= t < MARKET_CLOSE


def get_nasdaq_change():
    ticker = yf.Ticker("NQ=F")
    hist = ticker.history(period="5d", interval="1h")
    hist.index = hist.index.tz_convert(ET)

    # Find the most recent 4 PM ET bar (RTH settlement reference)
    rth_closes = hist[hist.index.hour == 16]
    if rth_closes.empty:
        raise ValueError("No RTH settlement bar found")
    prev_close = rth_closes["Close"].iloc[-1]
    latest     = hist["Close"].iloc[-1]
    return (latest - prev_close) / prev_close * 100


def set_color(device, color):
    url = f"http://{device['ip']}:16021/api/v1/{device['token']}/state"
    payload = {
        "on":         {"value": True},
        "hue":        {"value": color["hue"]},
        "sat":        {"value": color["sat"]},
        "brightness": {"value": color["brightness"]},
    }
    resp = requests.put(url, json=payload, timeout=5)
    resp.raise_for_status()


def update_lights():
    change_pct = get_nasdaq_change()
    color      = GREEN if change_pct >= 0 else RED
    direction  = "UP" if change_pct >= 0 else "DOWN"
    color_name = "green" if change_pct >= 0 else "red"

    log(f"Nasdaq {direction} {abs(change_pct):.2f}% — setting lights to {color_name}")

    for device in DEVICES:
        try:
            set_color(device, color)
            log(f"  {device['name']}: OK")
        except Exception as e:
            log(f"  {device['name']}: FAILED — {e}")


def main():
    log("Nanoleaf Nasdaq tracker started. Checking every 5 minutes during market hours.")
    while True:
        if is_market_open():
            try:
                update_lights()
            except Exception as e:
                log(f"Error fetching Nasdaq data: {e}")
        else:
            now = datetime.now(ET)
            # Exit cleanly after market close on weekdays
            if now.weekday() < 5 and (now.hour, now.minute) >= MARKET_CLOSE:
                log("Market closed. Shutting down.")
                break
            else:
                log(f"Market not open yet. Waiting...")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
