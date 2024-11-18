from stock import Stock

from logger import logger

memestop = Stock("GME")
memestop.obtain_market_data()
for i in range(1, 10):
    logger.info(
        f"Het verschil in volume t.o.v. {i} minuten geleden was {memestop.get_change_in_volume(i)} {memestop.get_price_movement(i)}"
    )

time_intervals = [1,2,3,4,5,6,7,8,9,10]  
volume_threshold = 0.2
price_threshold = 0 

memestop.check_market_conditions(time_intervals, volume_threshold, price_threshold)