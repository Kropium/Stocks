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

        for i in range(1, minutes_ago + 1):
            if market_data[-i].volume == 0 or market_data[-(i + 1)].volume == 0:
                logger.debug(
                    f"Volume is zero at index {-(i+1)} or {-(i)}, cannot calculate volume change."
                )
                volume_changes.append(0)  # Append 0 if any volume is 0
                continue

            absolute_verschil = market_data[-i].volume - market_data[-(i + 1)].volume
            if market_data[-(i + 1)].volume == 0:
                volume_changes.append(0)
                continue

            relatieve_verschil = round(absolute_verschil / market_data[-(i + 1)].volume, 6)
            logger.debug(
                f"Comparing minute -{i} with minute -{i+1}: Oude volume: {market_data[-(i + 1)].volume}, nieuwe volume: {market_data[-i].volume}"
            )
            logger.debug(f"Verschil: {absolute_verschil} ({relatieve_verschil*100}%)")
            volume_changes.append(relatieve_verschil)

        return volume_changes

    def get_price_movement(self, minutes_ago: int) -> list[int | float]:
        if len(self.market_data) < minutes_ago + 1:
            logger.debug("Onvoldoende data om dit te doen")
            return []

        market_data = list(self.market_data.values())
        price_movements = []

        for i in range(1, minutes_ago + 1):
            if market_data[-i].close == 0 or market_data[-(i + 1)].close == 0:
                logger.debug(
                    f"Close price is zero at index {-(i+1)} or {-(i)}, cannot calculate price movement."
                )
                price_movements.append(0)
                continue

            prijs_verschil = market_data[-i].close - market_data[-(i + 1)].close
            if market_data[-(i + 1)].close == 0:
                price_movements.append(0)
                continue

        relatieve_verschil_prijs = round(prijs_verschil / market_data[-(i + 1)].close, 6)
        logger.debug(
            f"Comparing minute -{i} with minute -{i+1}: Oude close: {market_data[-(i + 1)].close}, nieuwe close: {market_data[-i].close}"
        )
        logger.debug(f"Verschil: {prijs_verschil} ({relatieve_verschil_prijs*100}%)")
        price_movements.append(relatieve_verschil_prijs)

        return price_movements

    def check_market_conditions(
        self, time_intervals: list, volume_threshold: float, price_threshold: float
    ):
        for minutes_ago in time_intervals:
            price_movements = self.get_price_movement(minutes_ago)

            if not price_movements:
                logger.warning(f"No price movements found for {minutes_ago} minutes ago.")
                continue

            for i, price_movement in enumerate(price_movements, start=1):
                if price_movement >= price_threshold:
                    logger.info(
                        f"Price movement for {minutes_ago - i + 1} minutes ago: {price_movement * 100:.2f}% exceeds threshold."
                    )

            volume_changes = self.get_change_in_volume(minutes_ago)

            if not volume_changes:
                logger.warning(f"No volume changes found for {minutes_ago} minutes ago.")
                continue

            for i, volume_change in enumerate(volume_changes, start=1):
                if volume_change >= volume_threshold:
                    logger.info(
                        f"Volume change for {minutes_ago - i + 1} minutes ago: {volume_change * 100:.2f}% exceeds threshold."
                    )

    def __repr__(self):
        return f"{self.ticker}"
