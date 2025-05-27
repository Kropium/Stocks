import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from db_models import MarketData
from db_setup import SessionLocal
from datetime import datetime, timedelta

def calculate_rsi(data, window=14):
    delta = data['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=window, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9): 
    data['ema_12'] = data['close'].ewm(span=fast_period, adjust=False).mean()
    data['ema_26'] = data['close'].ewm(span=slow_period, adjust=False).mean()

    # MACD is the difference between the two EMAs
    data['macd'] = data['ema_12'] - data['ema_26']

    # Signal line is the 9-period EMA of the MACD line
    data['macd_signal'] = data['macd'].ewm(span=signal_period, adjust=False).mean()

    return data


def calculate_ema(data, fast_period=12, slow_period=26):
    # Calculate the 12-period EMA and 26-period EMA
    data['ema_12'] = data['close'].ewm(span=fast_period, adjust=False).mean()
    data['ema_26'] = data['close'].ewm(span=slow_period, adjust=False).mean()

    return data


def calculate_indicators_for_last_minute():
    # Start a session to interact with the database
    session = SessionLocal()

    # Get the most recent timestamp (last minute)
    latest_timestamp = session.query(MarketData.timestamp).order_by(MarketData.timestamp.desc()).first()
    if not latest_timestamp:
        print("No data found in the database.")
        return
    
    latest_timestamp = latest_timestamp[0]
    start_time = latest_timestamp - timedelta(minutes=26)
    market_data = session.query(MarketData).filter(MarketData.timestamp >= start_time).all()

    if len(market_data) < 26:
        print("Not enough data to calculate indicators (missing data). Trying to forward-fill missing data.")
        missing_minutes = 26 - len(market_data)
        last_data_point = market_data[-1] if market_data else None
        if last_data_point:
            for _ in range(missing_minutes):
                market_data.append(last_data_point)
        else:
            print("Cannot forward-fill as there's no available data.")
            return

    data = pd.DataFrame([(d.timestamp, d.close, d.stock_id) for d in market_data], columns=["timestamp", "close", "stock_id"])

    data['rsi'] = calculate_rsi(data, window=14)  # RSI requires at least 14 periods
    data = calculate_macd(data)  # MACD requires at least 26 periods
    data = calculate_ema(data)  # EMA requires at least 26 periods

    if len(data) < 14:  
        prev_day_data = session.query(MarketData).filter(MarketData.timestamp < latest_timestamp).order_by(MarketData.timestamp.desc()).limit(14).all()
        prev_day_data = pd.DataFrame([(d.timestamp, d.close, d.stock_id) for d in prev_day_data], columns=["timestamp", "close", "stock_id"])
        data = pd.concat([prev_day_data, data])

    last_record = data.iloc[-1] 
    stock_id = last_record['stock_id']
    timestamp = last_record['timestamp']

    # Fetch the market data record that corresponds to the most recent minute
    market_data_record = session.query(MarketData).filter_by(stock_id=stock_id, timestamp=timestamp).first()
    if market_data_record:
        market_data_record.rsi = last_record['rsi']
        market_data_record.macd = last_record['macd']
        market_data_record.macd_signal = last_record['macd_signal']
        market_data_record.ema_12 = last_record['ema_12']
        market_data_record.ema_26 = last_record['ema_26']

        # Commit the changes to the database
        session.commit()

    session.close()


if __name__ == "__main__":
    calculate_indicators_for_last_minute()
