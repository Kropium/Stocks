import pyodbc
from concurrent.futures import ThreadPoolExecutor, as_completed

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=DESKTOP-7Q8DA2Q\\SQLEXPRESS;"
    "Database=stock_db;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def test_db_connection(i):
    try:
        with pyodbc.connect(conn_str, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Thread {i}: Success")
            return True
    except Exception as e:
        print(f"Thread {i}: Failed - {e}")
        return False

max_threads = 200  # You can adjust this to stress-test your SQL Server
successes = 0

with ThreadPoolExecutor(max_workers=max_threads) as executor:
    futures = [executor.submit(test_db_connection, i) for i in range(max_threads)]
    for f in as_completed(futures):
        if f.result():
            successes += 1

print(f"\n Successful connections: {successes}/{max_threads}")
