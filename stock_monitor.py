import time
import json
import multiprocessing
from logger import logger
from wallet import VirtualWallet
from stock_db import StockRaw  # Updated import: new class with DB integration

def monitor_stock(ticker):
    volume_threshold = 0.25
    price_threshold = 0.01
    cooldown_period = 360 

    wallet = VirtualWallet(filename="wallet.json")
    logger.debug(f"Initial wallet balance: {wallet.check_balance()}")

    if ticker in wallet.sell_cooldowns:
        last_sell_time = wallet.sell_cooldowns[ticker]
        if time.time() - last_sell_time < cooldown_period:
            remaining = cooldown_period - (time.time() - last_sell_time)
            logger.info(f"Cooldown active for {ticker}. Try again in {remaining:.2f} seconds.")
            return

    stock = StockRaw(ticker)
    stock.fetch_market_data_from_db()


    if ticker in wallet.stocks:
        snapshots = stock.get_last_two_snapshots()
        if not snapshots or not snapshots[-1].close:
            logger.warning(f"Not enough or invalid data to evaluate selling {ticker}.")
            return

        if wallet.sell_stock(stock):
            logger.info(f"Sold {ticker} based on trailing stop loss.")
            wallet.sell_cooldowns[ticker] = time.time()
            wallet.save_wallet(wallet.filename)
        else:
            logger.info(f"Trailing stop loss not triggered for {ticker}.")
        return

    # If not owned, check for buy signal
    logger.info(f"Monitoring stock: {ticker} for buying conditions.")
    change = stock.get_change_since_last_retrieved()
    if not change:
        logger.info(f"Insufficient data to evaluate buying {ticker}.")
        return

    price_change = change.get("price_change")
    volume_change = change.get("volume_change")

    if (price_change is not None and abs(price_change) > price_threshold and
        volume_change is not None and abs(volume_change) > volume_threshold):
        
        logger.info(f"Buy conditions met for {ticker} (Δprice={price_change}, Δvolume={volume_change}).")
        if wallet.buy_stock(stock, minutes_ago=1):
            wallet.save_wallet(wallet.filename)
    else:
        logger.info(f"Buy conditions NOT met for {ticker} (Δprice={price_change}, Δvolume={volume_change}).")

    logger.debug(f"Balance: {wallet.check_balance()}")
    logger.debug(f"Portfolio: {wallet.check_portfolio()}")


def monitor_stocks_parallel():
    tickers = [
        "ADTX", "BIVI", "IMUX", "AUR", "CAPT", "THTX", "BHAT", "BLUE", "SILO", "SANA",
        "AEON", "IFBD", "PMNT", "RAPT", "BNGO", "ALZN", "SAGE", "ACRV", "RSLS", "TIVC",
        "PSTX", "BJDX", "NDRA", "GOVX", "MBIO", "ATAI", "CELU", "PRFX", "TOVX", "ONCT",
        "LGVN", "PHGE", "WINT", "HLVX", "BCTX", "BNOX", "EVAX", "BLRX", "IMRX", "CTOR",
        "AILE", "AVTX", "AQB", "ICCT", "CYN", "KITT", "SLDP", "NLSP", "GCTK", "VINC",
        "KPTI", "MITQ", "PTPI", "SURG", "PRPH", "CRKN", "MEGL", "BMRA", "ENSC", "CTXR",
        "EKSO", "INVZ", "HOTH", "XAIR", "PHIO", "MYSZ", "LPSN", "MLGO", "LPTX", "OCEA",
        "GV", "WTO", "APVO"
    ]

    max_cores = int(multiprocessing.cpu_count() * 0.7)
    chunk_size = len(tickers) // max_cores + 1
    ticker_chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]

    while True:
        with multiprocessing.Pool(processes=max_cores) as pool:
            pool.map(monitor_stock, [ticker for chunk in ticker_chunks for ticker in chunk])

        logger.info("Round complete. Restarting monitoring cycle after delay.")
        time.sleep(15)


if __name__ == "__main__":
    monitor_stocks_parallel()
