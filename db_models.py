from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class  Stock(Base):
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    
    ticker = Column(String(16), unique=True, nullable=False)
    
    market_data = relationship('MarketData', back_populates='stock', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<DBStock(ticker={self.ticker}, id={self.id})>"

class MarketData(Base):
    __tablename__ = 'market_data'

    id = Column(Integer, primary_key=True)
    
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)  
    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    adj_close = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    open = Column(Float)
    volume = Column(Float)
    rsi = Column(Float)
    macd = Column(Float) 
    macd_signal = Column(Float) 
    ema_12 = Column(Float) 
    ema_26 = Column(Float)


    stock = relationship('Stock', back_populates='market_data')

    def __repr__(self):
        return f"<MarketData(stock_id={self.stock_id}, timestamp={self.timestamp}, close={self.close})>"


engine = create_engine('sqlite:///stock_data.db', echo=False)


SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Function to create tables based on the defined models"""
    try:
        Base.metadata.create_all(engine)  # This will create the tables in the database
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

if __name__ == '__main__':
    init_db()
