from datetime import datetime, date, timedelta
import pandas as pd
import yfinance as yf
from logger import logger
from db_models import Stock, MarketData
from db_setup import SessionLocal  

class StockRaw:
    def __init__(self, ticker: str):
        self.ticker: str = ticker
        self.raw_market_data: pd.DataFrame = pd.DataFrame()
        self.market_data: dict[datetime, MarketData] = {}

    def obtain_market_data(self, start: datetime | date | str = datetime.now().date(), end: datetime | date | str = datetime.now()) -> None:
        """Download stock data from Yahoo Finance and structure it."""
        logger.debug(f"Begin downloading data for {self.ticker}")
        fetched_data = yf.download(self.ticker, start=start, end=end, interval="1m")
        self.raw_market_data = fetched_data
        logger.debug("Data downloaded")
        self.structure_market_data()

    def structure_market_data(self):
        """Process the downloaded market data and structure it."""
        logger.debug("Structuring market data")

        if isinstance(self.raw_market_data.columns, pd.MultiIndex):
            self.raw_market_data = self.raw_market_data.xs(key=self.ticker, axis=1, level=1)
            logger.debug(f"Extracted data for {self.ticker} from MultiIndex")

        for timestamp, row in self.raw_market_data.iterrows():
            try:
                open_price = row["Open"]
                high_price = row["High"]
                low_price = row["Low"]
                close_price = row["Close"]
                volume = row["Volume"]
                adj_close_price = row.get("Adj Close", close_price)
                logger.debug(f"Row at {timestamp}: Open={open_price}, Close={close_price}, Volume={volume}")
                if any(pd.isna([open_price, high_price, low_price, close_price, volume])):
                    logger.warning(f"Missing data for {timestamp}")
                    continue

                # Store the data in the market_data dictionary
                self.market_data[timestamp] = MarketData(
                    timestamp=timestamp,
                    adj_close=adj_close_price,
                    close=close_price,
                    high=high_price,
                    low=low_price,
                    open=open_price,
                    volume=volume,
                )

            except KeyError as e:
                logger.error(f"Missing column: {e}")
            except Exception as e:
                logger.error(f"Error structuring data: {e}")
    
    def save_to_db(self):
        session = SessionLocal()  # Create a new session

        try:
            # Check if the stock already exists in the DB
            db_stock = session.query(Stock).filter_by(ticker=self.ticker).first()

            if not db_stock:
                db_stock = Stock(ticker=self.ticker)
                session.add(db_stock)
                session.commit()  # Commit to get the stock ID
                logger.info(f"Added new stock: {self.ticker}")

            # Collect all MarketData entries and associate them with the stock
            market_data_objects = []
            for timestamp, md in self.market_data.items():
                # Check if the data already exists for the stock and timestamp
                existing_data = session.query(MarketData).filter_by(stock_id=db_stock.id, timestamp=md.timestamp).first()
                if existing_data:
                    logger.debug(f"Skipping duplicate data for {self.ticker} at {timestamp}")
                    continue

                db_md = MarketData(
                    stock_id=db_stock.id,
                    timestamp=md.timestamp,
                    adj_close=md.adj_close,
                    close=md.close,
                    high=md.high,
                    low=md.low,
                    open=md.open,
                    volume=md.volume,
                    retrieved_at=datetime.utcnow()
                )          
                market_data_objects.append(db_md)

            if market_data_objects:
                session.add_all(market_data_objects)

            session.commit()
            logger.info(f"Saved market data for {self.ticker} to database.")
            logger.debug(f"Preparing to insert MarketData for {timestamp}, volume={md.volume}")

        except Exception as e:
            logger.error(f"Failed to save {self.ticker} to DB: {e}")
            session.rollback() 
        finally:
            session.close() 


    def fetch_market_data_from_db(self):
        """Fetch the last 5 minutes of market data from the database."""
        session = SessionLocal()

        try:
            db_stock = session.query(Stock).filter_by(ticker=self.ticker).first()

            if not db_stock:
                logger.warning(f"Stock {self.ticker} not found in the database.")
                return

            now = datetime.utcnow()
            five_minutes_ago = now - timedelta(minutes=5)

            db_market_data = session.query(MarketData) \
                .filter(MarketData.stock_id == db_stock.id) \
                .filter(MarketData.timestamp >= five_minutes_ago) \
                .order_by(MarketData.timestamp.desc()) \
                .all()

            self.market_data = {md.timestamp: md for md in db_market_data}

            logger.info(f"Successfully fetched {len(self.market_data)} market data points for {self.ticker} from the database.")
        except Exception as e:
            logger.error(f"Error fetching data for {self.ticker} from the database: {e}")
        finally:
            session.close()
    
    def get_last_two_snapshots(self) -> list[MarketData]:
        """Return the last two data points based on retrieved_at timestamps."""
        if len(self.market_data) < 2:
            logger.debug(f"Not enough data points to get last two snapshots for {self.ticker}.")
            return []

        sorted_data = sorted(self.market_data.values(), key=lambda x: x.retrieved_at)
        return sorted_data[-2:]

    def get_change_since_last_retrieved(self) -> dict | None:
        """Calculate price and volume change between last two retrievals."""
        snapshots = self.get_last_two_snapshots()
        if len(snapshots) < 2:
            logger.debug(f"Not enough snapshots to calculate change for {self.ticker}.")
            return None

        prev, curr = snapshots

        result = {
            "price_change": None,
            "volume_change": None,
            "time_diff": (curr.retrieved_at - prev.retrieved_at)
        }

        try:
            if prev.close and curr.close:
                result["price_change"] = round((curr.close - prev.close) / prev.close, 6)

            if prev.volume and curr.volume:
                result["volume_change"] = round((curr.volume - prev.volume) / prev.volume, 6)

        except Exception as e:
            logger.error(f"Error calculating change since last retrieved for {self.ticker}: {e}")

        return result

    def get_price(self, key="close") -> float:
        """Return the most recent price by key (e.g., 'close', 'open')."""
        if not self.market_data:
            return 0.0
        latest = sorted(self.market_data.values(), key=lambda x: x.timestamp)[-1]
        return getattr(latest, key.lower(), 0.0) or 0.0

    def __repr__(self):
        return f"Stock({self.ticker})"