import yfinance as yf
import ccxt
import pandas as pd
import os
from tqdm import tqdm # Import tqdm

# Ensure the data/raw directory exists
os.makedirs("data/raw", exist_ok=True)

def fetch_yfinance_btc():
    """Fetches historical BTC-USD data from Yahoo Finance."""
    print("Fetching data from yfinance...")
    try:
        ticker = yf.Ticker("BTC-USD")
        # Get max history with progress bar
        history = ticker.history(period="max")
        # Add tqdm progress bar for saving (though saving is usually fast)
        with tqdm(total=1, desc="Saving yfinance data") as pbar:
            history.to_csv("data/raw/btc_market_data_yfinance.csv")
            pbar.update(1)
        print(f"Saved yfinance data: {len(history)} rows")
    except Exception as e:
        print(f"Error fetching from yfinance: {e}")

def fetch_ccxt_btc():
    """Fetches recent hourly BTC/USDT data from Binance."""
    print("Fetching data from ccxt (Binance)...")
    try:
        exchange = ccxt.binance()
        # Fetch 1-hour (1h) OHLCV data, increase limit if possible/needed
        # Use tqdm for fetching multiple chunks if needed, here just for saving
        limit = 1000 # Fetch more if needed, check exchange limits
        print(f"Fetching last {limit} hourly bars...")
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=limit)

        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        with tqdm(total=1, desc="Saving ccxt data") as pbar:
            df.to_csv("data/raw/btc_market_data_binance_hourly.csv", index=False)
            pbar.update(1)
        print(f"Saved ccxt data: {len(df)} rows")
    except ccxt.NetworkError as e:
        print(f"CCXT Network Error: {e}. Check connection or exchange status.")
    except ccxt.ExchangeError as e:
        print(f"CCXT Exchange Error: {e}. Check API keys or symbol.")
    except Exception as e:
        print(f"An unexpected error occurred with ccxt: {e}")

if __name__ == "__main__":
    fetch_yfinance_btc()
    fetch_ccxt_btc()
