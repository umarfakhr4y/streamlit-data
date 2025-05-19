import mysql.connector
import streamlit as st

def create_connection():
    """Fungsi untuk membuat koneksi ke database MySQL."""
    try:
        conn = mysql.connector.connect(
            host="localhost",        # Ganti dengan host database Anda
            user="root",             # Ganti dengan username MySQL Anda
            password="",  # Ganti dengan password MySQL Anda
            database="login_app"     # Ganti dengan nama database Anda
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Gagal terhubung ke database: {e}")
        return None
