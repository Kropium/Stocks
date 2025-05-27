from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import Base  # Your ORM models
from sqlalchemy.exc import SQLAlchemyError

SQLALCHEMY_DATABASE_URL = (
  "mssql+pyodbc://@DESKTOP-7Q8DA2Q\\SQLEXPRESS/stock_db?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")
        raise

# Run this to create tables
if __name__ == "__main__":
    init_db()
