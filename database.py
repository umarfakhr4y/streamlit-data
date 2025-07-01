import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
import pandas as pd


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

def fetch_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parfum_table")
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data)

# Fungsi menambahkan data ke database
def insert_data(varian_name, fragrant, formula, aquadest, alkohol, gender, jenis, ukuran, harga):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO parfum_table (VARIAN_NAME, FRAGRANT, FORMULA, AQUADEST, ALKOHOL, GENDER, JENIS, UKURAN, HARGA)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (varian_name, fragrant, formula, aquadest, alkohol, gender, jenis, ukuran, harga)
    cursor.execute(query, values)
    conn.commit()
    conn.close()

# Fungsi memperbarui data di database
def update_data(id, varian_name, fragrant, formula, aquadest, alkohol, gender, jenis, ukuran, harga):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        UPDATE parfum_table
        SET VARIAN_NAME = %s, FRAGRANT = %s, FORMULA = %s, AQUADEST = %s, ALKOHOL = %s, GENDER = %s, JENIS = %s, UKURAN = %s, HARGA = %s
        WHERE id = %s
    """
    values = (varian_name, fragrant, formula, aquadest, alkohol, gender, jenis, ukuran, harga, id)
    cursor.execute(query, values)
    conn.commit()
    conn.close()

# Fungsi menghapus data dari database
def delete_data(id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "DELETE FROM parfum_table WHERE id = %s"
    cursor.execute(query, (id,))
    conn.commit()
    conn.close()
