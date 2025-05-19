import streamlit as st
from database import get_connection

def login_page():
    st.title("Login Admin")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.is_logged_in = True  # Status login berhasil
            st.success("Login berhasil! Selamat datang di dashboard.")
            st.rerun()  # Perbaikan di sini: st.rerun menggantikan st.experimental_rerun
        else:
            st.error("Username atau password salah.")

def authenticate(username, password):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            return bool(result)  # True jika login berhasil
        except Exception as e:
            st.error(f"Terjadi kesalahan database: {e}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            conn.close()
    else:
        st.error("Gagal menyambungkan ke database.")
        return False
