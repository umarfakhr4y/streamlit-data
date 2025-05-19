import streamlit as st
import mysql.connector
import pandas as pd

# Koneksi ke database
def get_connection():
    return mysql.connector.connect(
        host="localhost",  # Sesuaikan dengan host database Anda
        user="root",       # Ganti dengan username MySQL Anda
        password="",       # Ganti dengan password MySQL Anda
        database="login_app"
    )

# Fungsi membaca data dari database
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

# Dashboard dengan CRUD
def dashboard_page():
    st.title("Dashboard Pengelolaan Data Parfum")
    st.subheader("Tabel Data Parfum")
    
    # Menampilkan data
    data = fetch_data()
    st.dataframe(data)
    
    # Form untuk menambah atau memperbarui data
    with st.form("form_data"):
        st.write("Masukkan Data Parfum:")
        id = st.text_input("ID (kosongkan untuk data baru)")
        varian_name = st.text_input("Varian Name")
        fragrant = st.text_input("Fragrant")
        formula = st.number_input("Formula", min_value=0.0)
        aquadest = st.number_input("Aquadest", min_value=0.0)
        alkohol = st.number_input("Alkohol", min_value=0.0)
        gender = st.selectbox("Gender", ["CEWE", "COWO", "UNISEX"])
        jenis = st.text_input("Jenis")
        ukuran = st.number_input("Ukuran", min_value=0.0)
        harga = st.number_input("Harga", min_value=0.0)
        
        submit_button = st.form_submit_button("Simpan Data")
        if submit_button:
            if id:
                update_data(id, varian_name, fragrant, formula, aquadest, alkohol, gender, jenis, ukuran, harga)
                st.success("Data berhasil diperbarui!")
            else:
                insert_data(varian_name, fragrant, formula, aquadest, alkohol, gender, jenis, ukuran, harga)
                st.success("Data berhasil ditambahkan!")
    
    # Menghapus data
    st.subheader("Hapus Data")
    delete_id = st.text_input("Masukkan ID untuk dihapus")
    if st.button("Hapus Data"):
        if delete_id:
            delete_data(delete_id)
            st.success(f"Data dengan ID {delete_id} berhasil dihapus!")
        else:
            st.error("Masukkan ID untuk menghapus data.")
    
    # Refresh data
    if st.button("Muat Ulang Data"):
        st.experimental_rerun()

if __name__ == "__main__":
    dashboard_page()
