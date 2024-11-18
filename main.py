from stock import Stock

from logger import logger

memestop = Stock("GME")
memestop.obtain_market_data()
for i in range(1, 20):
    logger.info(
        f"Het verschil in volume t.o.v. {i} minuten geleden was {memestop.get_change_in_volume(i)}"
    )

#test
