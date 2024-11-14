class MarketData:
    def __init__(self, timestamp,
                 adj_close: float,
                 close: float, high: float, low: float, open: float, volume: float):
        self.timestamp = timestamp
        self.adj_close = adj_close
        self.close = close
        self.high = high
        self.low = low
        self.open = open
        self.volume = volume

    def __repr__(self):
            # Return a string with all the values for easy reading
            return (f"MarketData@timestamp={self.timestamp}: "
                    f"Open={self.open}, Close={self.close}, "
                    f"High={self.high}, Low={self.low}, Volume={self.volume})")