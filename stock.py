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

    def obtain_market_data(
        self,
        start: datetime | date | str = datetime.now().date(),
        end: datetime | date | str = datetime.now(),
    ) -> None:
        """Download de data en opslaan als attribute market_data"""
        logger.debug(f"begin met downloaden van data")
        fetched_data = yf.download(self.ticker, start=start, end=end, interval="1m")
        self.raw_market_data = fetched_data
        logger.debug(f"Data gedownload")
        self.structure_market_data()

    def structure_market_data(self):
        logger.debug(f"Data structureren")
        for timestamp, row in self.raw_market_data.iterrows():
            self.market_data[timestamp] = MarketData(timestamp, *row)
        logger.debug(f"Data staat klaar")

    def get_change_in_volume(self, minutes_ago: int) -> int | float:
        """Return relatieve verschil in volume"""
        if len(self.market_data) < minutes_ago:
            logger.debug(f"Onvoldoende data om dit te doen")
            return 0
        if minutes_ago == 0:
            return 0
        market_data = list(self.market_data.values())
        if market_data[-minutes_ago].volume == 0:
            return 0
        logger.debug(
            f"Oude volume: {market_data[-minutes_ago].volume}, nieuwe volume: {market_data[-2].volume}"
        )
        absolute_verschil = market_data[-2].volume - market_data[-minutes_ago].volume
        relatieve_verschil = round(absolute_verschil / market_data[-minutes_ago].volume, 6)
        logger.debug(f"Verschil: {absolute_verschil} ({relatieve_verschil*100}%)")
        return relatieve_verschil
    
    def get_price_movement(self, minutes_ago: int) -> int | float: 
        """Return verschil in prijs"""
        if len(self.market_data) < minutes_ago:
            logger.debug(f"Onvoldoende data om dit te doen")
            return 0 
        if minutes_ago == 0:
            return 0
        market_data = list(self.market_data.values())
        if market_data[-minutes_ago].close == 0:
            return 0
        logger.debug(
            f"Oude close: {market_data[-minutes_ago].close}, nieuwe close: {market_data[-2].close}"
        )
        prijs_verschil = market_data[-2].close - market_data[-minutes_ago].close
        relatieve_verschil_prijs = round(prijs_verschil / market_data[-minutes_ago].close, 6)
        logger.debug(f"Verschil: {prijs_verschil} ({relatieve_verschil_prijs*100}%)")
        return relatieve_verschil_prijs
 
    def __repr__(self):
        return f"{self.ticker}"
