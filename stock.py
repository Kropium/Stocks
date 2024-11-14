from datetime import datetime, date

import pandas as pd
import yfinance as yf

from market_data import MarketData

from logger import logger


class Stock:
    def __init__(self, ticker: str):
        self.ticker: str = ticker
        self.raw_market_data: pd.DataFrame = pd.DataFrame()
        self.market_data: dict[datetime, MarketData] = {}

    def obtain_market_data(self,
                           start: datetime | date | str = datetime.now().date(),
                           end: datetime | date | str = datetime.now()) -> None:
        """Download de data en opslaan als attribute market_data"""
        logger.debug(f"Faka g begin met downloaden van data")
        fetched_data = yf.download(self.ticker,
                                   start=start,
                                   end=end,
                                   interval='1m')
        self.raw_market_data = fetched_data
        logger.debug(f"Data gedownload")
        self.structure_market_data()

    def structure_market_data(self):
        logger.debug(f"Data ff structureren")
        for timestamp, row in self.raw_market_data.iterrows():
            self.market_data[timestamp] = MarketData(timestamp, *row)
        logger.debug(f"Data staat klaar")

    def get_change_in_volume(self, minutes_ago: int) -> int | float:
        """Return relatieve verschil in volume"""
        if len(self.market_data) < minutes_ago:
            logger.debug(f"Onvoldoende data om dit te doen brada")
            return 0
        if minutes_ago == 0:
            return 0
        market_data = list(self.market_data.values())
        if market_data[-minutes_ago].volume == 0:
            return 0
        logger.debug(f"Oude volume: {market_data[-minutes_ago].volume}, nieuwe volume: {market_data[-2].volume}")
        absolute_verschil = market_data[-2].volume - market_data[-minutes_ago].volume
        relatieve_verschil = round(absolute_verschil/market_data[-minutes_ago].volume, 6)
        logger.debug(f"Verschil: {absolute_verschil} ({relatieve_verschil*100}%)")
        return relatieve_verschil

    def __repr__(self):
        return f"{self.ticker}"
