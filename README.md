[README.md](https://github.com/user-attachments/files/29100105/README.md)
# Nanoleaf Nasdaq Tracker

Automatically sets Nanoleaf lights to **green** or **red** based on whether NQ futures (NQ=F) are up or down from the previous session's close.

## How it works

- Runs every 5 minutes during NYSE market hours (9:30 AM – 4:00 PM ET, weekdays)
- Compares the current NQ futures price to the previous day's 4 PM ET settlement
- Sets both Nanoleaf devices to green if up, red if down
- Exits automatically at market close
- Logs every check to `nanoleaf.log` (keeps 7 days of history)

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Add your Nanoleaf device IPs and tokens in `main.py` under `DEVICES`

3. Schedule `main.py` to run at 9:00 AM ET on weekdays via Task Scheduler (Windows) or cron

## Dependencies

- `yfinance` — market data
- `requests` — Nanoleaf local HTTP API
- `pytz` — timezone handling
