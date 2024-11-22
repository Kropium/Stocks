from stock import Stock
from logger import logger
import time


def monitor_stocks():
    tickers = ["GME", "AAPL", "TSLA", "AMZN", "XCUR", "ADTX", "ALLR", "BIVI", "FGEN", "IMUX"]
    time_intervals = [
        1,
        2,
        3,
        4,
    ]
    volume_threshold = 0.2
    price_threshold = 0

    ticker_index = 0

    while True:
        current_ticker = tickers[ticker_index]
        logger.info(f"Monitoring stock: {current_ticker}")

        stock = Stock(current_ticker)
        stock.obtain_market_data()

        conditions_met = False

        for i in range(1, len(time_intervals) - 1):
            if stock.check_consecutive_conditions(
                time_intervals[i - 1], time_intervals[i], volume_threshold, price_threshold
            ):
                conditions_met = True
                logger.info(
                    f"Conditions met for {current_ticker} at time intervals {time_intervals[i-1]} and {time_intervals[i]}"
                )
                break
            elif stock.check_consecutive_conditions(
                time_intervals[i], time_intervals[i + 1], volume_threshold, price_threshold
            ):
                conditions_met = True
                logger.info(
                    f"Conditions met for {current_ticker} at time intervals {time_intervals[i]} and {time_intervals[i+1]}"
                )
                break

        if conditions_met:
            logger.info(f"Conditions met for {current_ticker}. Exiting monitoring loop.")
            break
        else:
            logger.info(f"Conditions not met for {current_ticker}. Moving to the next ticker.")
            ticker_index += 1

            if ticker_index >= len(tickers):
                ticker_index = 0

            time.sleep(3)
