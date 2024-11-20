from stock import Stock

from logger import logger

memestop = Stock("GME")
memestop.obtain_market_data()

time_intervals = [1, 2, 3, 4, 5]
volume_threshold = 0.2
price_threshold = 0

memestop.check_market_conditions(time_intervals, volume_threshold, price_threshold)
