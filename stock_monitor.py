from stock import Stock
from logger import logger
import time
from wallet import VirtualWallet
import pandas
import json


def monitor_stocks():
    tickers = [
        "AAPL",
        "TSLA",
        "AMZN",
        "ADTX",
        "ALLR",
        "BIVI",
        "FGEN",
        "IMUX",
        "GME",
        "CHWY",
        "QMCO",
        "BLUE",
        "ADAP",
        "ADPT",
        "GNPX",
        "MGNX",
        "CRBU" "BIOR",
        "OMGA",
        "REVB",
        "RAPT",
        "BNGO",
        "ATXI",
        "ALZN",
        "EVGN",
        "SAGE",
        "BFRI",
    ]

    time_intervals = [1, 2, 3, 4, 5, 6, 7, 8]
    volume_threshold = 0.3
    price_threshold = 0.002
    ticker_index = 0

    wallet = VirtualWallet(filename="wallet.json")

    logger.debug(f"Initial wallet balance: {wallet.check_balance()}")

    while True:
        for ticker, stock_data in wallet.stocks.items():
            stock = Stock(ticker)
            stock.obtain_market_data()

            if wallet.sell_stock(stock, profit_threshold=0.1, loss_threshold=0.05):
                logger.info(f"Successfully sold {ticker} based on profit or loss conditions.")

        current_ticker = tickers[ticker_index]
        if current_ticker in wallet.stocks:
            logger.info(f"Stock {current_ticker} already in the wallet. Skipping buy check.")
            ticker_index += 1
            if ticker_index >= len(tickers):
                ticker_index = 0
            time.sleep(1)
            continue
        logger.info(f"Monitoring stock: {current_ticker}")

        stock = Stock(current_ticker)
        stock.obtain_market_data()

        conditions_met = False

        # Check conditions for each time interval
        for i in range(1, len(time_intervals) - 1):
            if stock.check_consecutive_conditions(
                time_intervals[i - 1], time_intervals[i], volume_threshold, price_threshold
            ):
                conditions_met = True
                logger.info(
                    f"Conditions met for {current_ticker} at time intervals {time_intervals[i - 1]} and {time_intervals[i]}"
                )
                # Perform stock purchase and save wallet immediately after
                if wallet.buy_stock(stock, minutes_ago=1):
                    wallet.save_wallet(wallet.filename)  # Save wallet after purchase
                break
            elif stock.check_consecutive_conditions(
                time_intervals[i], time_intervals[i + 1], volume_threshold, price_threshold
            ):
                conditions_met = True
                logger.info(
                    f"Conditions met for {current_ticker} at time intervals {time_intervals[i]} and {time_intervals[i + 1]}"
                )
                # Perform stock purchase and save wallet immediately after
                if wallet.buy_stock(stock, minutes_ago=1):
                    wallet.save_wallet(wallet.filename)  # Save wallet after purchase
                break

        # Exit loop if conditions are met for the stock
        if conditions_met:
            logger.info(f"Conditions met for {current_ticker}. Exiting monitoring loop.")
            break
        else:
            logger.info(f"Conditions not met for {current_ticker}. Moving to the next ticker.")
            ticker_index += 1

            if ticker_index >= len(tickers):
                ticker_index = 0

            time.sleep(2)

    logger.debug(f"Current balance: {wallet.check_balance()}")
    logger.debug(f"Current portfolio: {wallet.check_portfolio()}")
