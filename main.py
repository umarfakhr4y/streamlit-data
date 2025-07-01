import streamlit as st
import pandas as pd  # Untuk manipulasi DataFrame jika diperlukan

from login import login_page
from dashboard import dashboard_page
from clustering import clustering_page
from prediction import prediction_page

def app():
    # Inisialisasi session_state jika belum ada
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "Login Admin"
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame()

    # Jika belum login, paksa user ke halaman login
    if not st.session_state.is_logged_in:
        st.session_state.page = "Login Admin"
        login_page()
        return  # Langsung keluar agar sidebar tidak dirender

    # Sidebar hanya ditampilkan jika sudah login
    st.sidebar.title("Menu Utama")
    if st.sidebar.button("🏠 Beranda", key="dashboard"):
        st.session_state.page = "Beranda"
    if st.sidebar.button("🔍 Clustering", key="clustering"):
        st.session_state.page = "Clustering"
    if st.sidebar.button("📊 Prediction", key="prediction"):
        st.session_state.page = "Prediction"
    if st.sidebar.button("🔒 Logout", key="logout"):
        st.session_state.is_logged_in = False
        st.session_state.page = "Login Admin"
        st.rerun()  # Penting! Untuk langsung rerender ke halaman login

    # Render halaman berdasarkan pilihan
    if st.session_state.page == "Beranda":
        dashboard_page()
    elif st.session_state.page == "Clustering":
        clustering_page()
    elif st.session_state.page == "Prediction":
        prediction_page()

# Menjalankan aplikasi Streamlit
if __name__ == "__main__":
    app()
