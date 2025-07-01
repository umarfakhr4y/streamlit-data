import streamlit as st
import pandas as pd
from database import fetch_data, insert_data, update_data, delete_data

def dashboard_page():
    st.title("Dashboard Pengelolaan Data Parfum")

    # --- STATE CONTROL ---
    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None
    if "varian_to_add" not in st.session_state:
        st.session_state.varian_to_add = ""
    if "cached_data" not in st.session_state:
        st.session_state.cached_data = fetch_data()

    # --- TAMPILKAN DATA ---
    st.subheader("Tabel Data Parfum")
    data = st.session_state.cached_data
    st.dataframe(data)

    # --- TAMBAH DATA 2 TAHAP ---
    st.subheader("Tambah Data Baru")
    if not st.session_state.varian_to_add:
        with st.form("form_nama_varian"):
            varian_input = st.text_input("Masukkan nama varian baru")
            lanjut = st.form_submit_button("Lanjutkan")
            if lanjut:
                if varian_input.strip():
                    st.session_state.varian_to_add = varian_input.strip()
                else:
                    st.warning("Nama varian tidak boleh kosong.")
    else:
        with st.form("form_lanjut_tambah"):
            st.markdown(f"**Varian:** `{st.session_state.varian_to_add}`")
            fragrant = st.text_input("Fragrant")
            formula = st.number_input("Formula", min_value=0.0)
            aquadest = st.number_input("Aquadest", min_value=0.0)
            alkohol = st.number_input("Alkohol", min_value=0.0)
            gender = st.selectbox("Gender", ["CEWE", "COWO", "UNISEX"])
            jenis = st.text_input("Jenis")
            ukuran = st.number_input("Ukuran", min_value=0.0)
            harga = st.number_input("Harga", min_value=0.0)
            simpan = st.form_submit_button("Simpan")
            if simpan:
                insert_data(st.session_state.varian_to_add, fragrant, formula, aquadest, alkohol, gender, jenis, ukuran, harga)
                st.success("Data berhasil ditambahkan.")
                st.session_state.varian_to_add = ""
                st.session_state.cached_data = fetch_data()  # Refresh data

        if st.button("Batalkan Tambah"):
            st.session_state.varian_to_add = ""

    # --- EDIT DATA ---
    st.subheader("Edit Data")
    varian_options = [f"{row['VARIAN_NAME']} ({row['id']})" for _, row in data.iterrows()]
    selected_label = st.selectbox("Pilih varian untuk diedit", varian_options)
    selected_id = int(selected_label.split("(")[-1].replace(")", ""))

    if st.button("Edit Data"):
        st.session_state.edit_id = selected_id

    if st.session_state.edit_id is not None:
        selected_row = data[data["id"] == st.session_state.edit_id].iloc[0]
        with st.form("form_edit_data"):
            st.write(f"Edit Data ID: {st.session_state.edit_id}")
            varian_name = st.text_input("Varian Name", value=selected_row["VARIAN_NAME"])
            fragrant = st.text_input("Fragrant", value=selected_row["FRAGRANT"])
            formula = st.number_input("Formula", value=float(selected_row["FORMULA"]), min_value=0.0)
            aquadest = st.number_input("Aquadest", value=float(selected_row["AQUADEST"]), min_value=0.0)
            alkohol = st.number_input("Alkohol", value=float(selected_row["ALKOHOL"]), min_value=0.0)
            gender = st.selectbox("Gender", ["CEWE", "COWO", "UNISEX"], index=["CEWE", "COWO", "UNISEX"].index(selected_row["GENDER"]))
            jenis = st.text_input("Jenis", value=selected_row["JENIS"])
            ukuran = st.number_input("Ukuran", value=float(selected_row["UKURAN"]), min_value=0.0)
            harga = st.number_input("Harga", value=float(selected_row["HARGA"]), min_value=0.0)
            simpan = st.form_submit_button("Simpan Perubahan")
            if simpan:
                update_data(st.session_state.edit_id, varian_name, fragrant, formula, aquadest, alkohol, gender, jenis, ukuran, harga)
                st.success("Data berhasil diperbarui.")
                st.session_state.cached_data = fetch_data()
                st.session_state.edit_id = None

        if st.button("Batalkan Edit"):
            st.session_state.edit_id = None

        # --- HAPUS DATA DENGAN DROPDOWN ---
    st.subheader("Hapus Data")

    # Buat daftar opsi dari data
    hapus_options = [f"{row['VARIAN_NAME']} (ID: {row['id']})" for _, row in data.iterrows()]
    
    # Tampilkan dropdown jika data tersedia
    if hapus_options:
        selected_delete = st.selectbox("Pilih varian untuk dihapus", hapus_options)
        delete_id = int(selected_delete.split("ID: ")[-1].replace(")", ""))

        if st.button("Hapus Varian Ini"):
            try:
                delete_data(delete_id)
                st.success(f"Data dengan ID {delete_id} berhasil dihapus.")
                st.session_state.cached_data = fetch_data()  # Refresh tabel
            except Exception as e:
                st.error(f"Gagal menghapus data: {e}")
    else:
        st.info("Tidak ada data yang bisa dihapus.")


    # --- REFRESH MANUAL (opsional) ---
    if st.button("Muat Ulang Data"):
        st.session_state.cached_data = fetch_data()
        st.success("Data berhasil dimuat ulang.")
