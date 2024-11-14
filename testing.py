import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

current_time = datetime.now()
current_time = current_time.replace(microsecond=0)
time_minus10 = current_time - timedelta(minutes=3370)

# Define the stock symbol and time range
symbol = 'AAPL' 
start_date = time_minus10
end_date = current_time

data = yf.download(symbol, start=start_date, end=end_date, interval='1m')

volume_data = data[['Volume']]
High_data = data[['High']]
low_data = data[['Low']]

df = data


p = float((df.iloc[-2, 2]) - (df.iloc[-1, 2]))

x = df.iloc[-1, 5]
y = df.iloc[-2, 5]

def volume_difference(old_volume, new_volume):
    if old_volume == 0:
        return ("No volume")

    difference = new_volume - old_volume
    percentage_difference = (difference / old_volume) * 100

    return percentage_difference

old_volume = x
new_volume = y
result = volume_difference(new_volume, old_volume)

print(f"Volume difference is {result}% with a volume of {x} and a price difference off {p}")
