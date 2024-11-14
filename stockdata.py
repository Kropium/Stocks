import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


class Stock:
    def __init__(self, symbol, timestamp, open_price, close_price, high, low, volume):
        self.symbol = symbol
        self.timestamp = pd.to_datetime(timestamp)
        self.open_price = open_price
        self.close_price = close_price
        self.high = high
        self.low = low
        self.volume = volume

def __repr__(self):
        return (f"Stock(symbol={self.symbol}, timestamp={self.timestamp}, "
                f"Open={self.open_price}, Close={self.close_price}, "
                f"High={self.high}, Low={self.low}, Volume={self.volume})")

current_time = datetime.now()
current_time = current_time.replace(microsecond=0)
time_minus10 = current_time - timedelta(minutes=370)

# Define the stock symbol and time range
symbol = 'GME' 
start_date = time_minus10
end_date = current_time

data = yf.download(symbol, start=start_date, end=end_date, interval='1m')

stocks = []

for timestamp, row in data.iterrows():
    stock = Stock(
        symbol='GME',
        timestamp=timestamp,  
        open_price=row['Open'],
        close_price=row['Close'],
        high=row['High'],
        low=row['Low'],
        volume=row['Volume']
    )
    stocks.append(stock)

print(stocks[-3].volume, stocks[-2].volume)


def volume_difference(old_volume, new_volume):

    difference = new_volume - old_volume
    percentage_difference = (difference / old_volume) * 100

    return percentage_difference

old_volume = (stocks[-2].volume)
new_volume = (stocks[-3].volume)
result = float(volume_difference(new_volume, old_volume))

print(result)

#class StockMarketChecker:
    #def __init__(self, stocks):
        #self.stocks = stocks  # List of Stock objects 

   # def loop_until_desired_stock(self):
        #condition_met = False
        #attempts = 0 

#while not condition_met and attempts < len(self.stocks):  

#if self.check_conditions(stock):
# Do something here, create function to notify
#condition_met = True
#else:
# continue searching in list of stocks
#attempts += 1

#def check_conditions(self, stock):
    #return stock.price > 100 and stock.volume > 1000 and stock.trend == "up"
