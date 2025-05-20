import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine

def get_connection():
    """Membuat koneksi ke database MySQL."""
    try:
        conn = mysql.connector.connect(
            host='localhost',        # Ganti dengan host MySQL Anda
            database='login_app',  # Ganti dengan nama database Anda
            user='root',             # Ganti dengan username MySQL Anda
            password=''   # Ganti dengan password MySQL Anda
        )
        return conn
    except Error as e:
        print(f"Error saat menyambungkan ke database: {e}")
        return None

def get_sqlalchemy_engine():
    user = 'root'
    password = ''
    host = 'localhost'
    port = 3306
    database = 'login_app'

    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
    return engine