import pyodbc

# Adjusted connection string with TrustServerCertificate
conn_str = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-7Q8DA2Q\\SQLEXPRESS;DATABASE=stock_db;UID=sa;PWD=your_password;TrustServerCertificate=yes;TRUSTED_CONNECTION=YES'

# Test connection
try:
    conn = pyodbc.connect(conn_str)
    print("Connection successful")
    conn.close()
except pyodbc.Error as e:
    print("Connection failed:", e)