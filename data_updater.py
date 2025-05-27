import time
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from stock_db import StockRaw as Stock
from logger import logger

tickers = [
    "BIVI", "IMUX", "AUR", "CAPT", "THTX",
    "BHAT", "BLUE", "SILO", "SANA", "AEON", "IFBD",
]

def update_latest_minute_data(ticker: str):
    """Fetch and update the most recent 1-minute candle for the given stock."""
    try:
        stock = Stock(ticker)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=3)
        stock.obtain_market_data(start=start_time, end=end_time)
        stock.save_to_db()
        logger.info(f"[{ticker}] Latest 1m candle saved.")
    except Exception as e:
        logger.error(f"[{ticker}] Error: {e}")

def run_parallel_data_updater():
    """Threaded data updater to download and update stock data as fast as possible."""
    max_threads = 100 
    logger.info(f"Starting threaded data updater with {max_threads} threads...")

    while True:
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(update_latest_minute_data, ticker) for ticker in tickers]
            for f in as_completed(futures):
                pass  

        elapsed = time.time() - start_time
        logger.info(f" Round complete in {elapsed:.2f}s. Sleeping for 15 seconds...\n")
        time.sleep(15)

if __name__ == "__main__":
    run_parallel_data_updater()
