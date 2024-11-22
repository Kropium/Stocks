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

    def get_change_in_volume(self, minutes_ago: int) -> list[int | float]:
        if len(self.market_data) < minutes_ago + 1:
            logger.debug("Onvoldoende data om dit te doen")
            return []

        market_data = list(self.market_data.values())
        volume_changes = []

        if market_data[-minutes_ago].volume == 0 or market_data[-(minutes_ago + 1)].volume == 0:
            logger.debug(
                f"Volume is zero at index {-(minutes_ago + 1)} or {-(minutes_ago)}, cannot calculate volume change."
            )
            volume_changes.append(0)
        else:
            absolute_verschil = (
                market_data[-minutes_ago].volume - market_data[-(minutes_ago + 1)].volume
            )
            relatieve_verschil = round(
                absolute_verschil / market_data[-(minutes_ago + 1)].volume, 6
            )
            logger.debug(
                f"Comparing minute -{minutes_ago} with minute -{minutes_ago + 1}: Oude volume: {market_data[-(minutes_ago + 1)].volume}, nieuwe volume: {market_data[-minutes_ago].volume}"
            )
            logger.debug(f"Verschil: {absolute_verschil} ({relatieve_verschil * 100}%)")
            volume_changes.append(relatieve_verschil)

        return volume_changes

    def get_price_movement(self, minutes_ago: int) -> list[int | float]:
        if len(self.market_data) < minutes_ago + 1:
            logger.debug("Onvoldoende data om dit te doen")
            return []

        market_data = list(self.market_data.values())
        price_movements = []

        if market_data[-minutes_ago].close == 0 or market_data[-(minutes_ago + 1)].close == 0:
            logger.debug(
                f"Close price is zero at index {-(minutes_ago + 1)} or {-(minutes_ago)}, cannot calculate price movement."
            )
            price_movements.append(0)
        else:
            prijs_verschil = (
                market_data[-minutes_ago].close - market_data[-(minutes_ago + 1)].close
            )
            relatieve_verschil_prijs = round(
                prijs_verschil / market_data[-(minutes_ago + 1)].close, 6
            )
            logger.debug(
                f"Comparing minute -{minutes_ago} with minute -{minutes_ago + 1}: Oude close: {market_data[-(minutes_ago + 1)].close}, nieuwe close: {market_data[-minutes_ago].close}"
            )
            logger.debug(f"Verschil: {prijs_verschil} ({relatieve_verschil_prijs * 100}%)")
            price_movements.append(relatieve_verschil_prijs)

        return price_movements

    def check_consecutive_conditions(
        self, interval_1: int, interval_2: int, volume_threshold: float, price_threshold: float
    ) -> bool:
        volume_change_1 = self.get_change_in_volume(interval_1)
        price_movement_1 = self.get_price_movement(interval_1)
        volume_change_2 = self.get_change_in_volume(interval_2)
        price_movement_2 = self.get_price_movement(interval_2)

        return (
            volume_change_1
            and volume_change_2
            and price_movement_1
            and price_movement_2
            and volume_change_1[0] > volume_threshold
            and volume_change_2[0] > volume_threshold
            and price_movement_1[0] > price_threshold
            and price_movement_2[0] > price_threshold
        )

    def __repr__(self):
        return f"Stock({self.ticker})"
