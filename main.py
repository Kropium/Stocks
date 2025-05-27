from logger import logger
from stock_monitor import monitor_stocks_parallel
from data_updater import run_parallel_data_updater


if __name__ == "__main__":
    monitor_stocks_parallel()
    run_parallel_data_updater()
