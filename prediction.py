import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sqlalchemy import inspect
from database import get_sqlalchemy_engine
import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def prediction_page():
    st.title("Prediksi Harga Parfum")

    engine = get_sqlalchemy_engine()
    inspector = inspect(engine)

    all_tables = inspector.get_table_names()
    clustering_tables = [t for t in all_tables if t.startswith("clustering_result_")]

    # uploaded_file = st.file_uploader("Unggah File CSV atau Excel dengan data harga parfum", type=["csv", "xlsx"])
    selected_table = st.selectbox("Pilih tabel clustering dari Database", clustering_tables)

    data = None

    if selected_table:
        try:
            data = pd.read_sql_table(selected_table, con=engine)
            st.success(f"Data dari tabel '{selected_table}' berhasil dimuat.")
            st.dataframe(data)
        except Exception as e:
            st.error(f"Gagal memuat data dari tabel: {e}")
            return

    if data is not None:
        st.subheader("Pilih kolom untuk digunakan dalam prediksi")
        feature_columns = st.multiselect("Pilih fitur (FORMULA, AQUADEST, ALKOHOL)", data.select_dtypes(include=["number"]).columns.tolist())
        target_column = st.selectbox("Pilih kolom target (Harga)", data.select_dtypes(include=["number"]).columns.tolist())

        if st.button("Latih Model"):
            if len(feature_columns) == 0 or target_column is None:
                st.error("Harap pilih kolom fitur dan target.")
                return

            if 'Cluster' not in data.columns:
                st.error("Kolom 'Cluster' tidak ditemukan dalam data.")
                return

            X_numerical = data[feature_columns].values
            y = data[target_column]

            # One-Hot Encoding untuk 'Cluster'
            encoder = OneHotEncoder(sparse_output=False, drop='first')
            X_encoded = encoder.fit_transform(data[['Cluster']])

            # Gabungkan fitur numerik dan encoded CLUSTER
            X_final = np.hstack((X_numerical, X_encoded))

            # Normalisasi semua fitur
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_final)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

            # Train model
            model = LinearRegression()
            model.fit(X_train, y_train)

            # Prediksi dan evaluasi
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            st.success("Model dilatih dengan sukses!")
            st.write(f"Mean Squared Error: {mse}")
            st.write(f"R² Score: {r2}")

            # Simpan ke session_state
            st.session_state.model = model
            st.session_state.scaler = scaler
            st.session_state.encoder = encoder
            st.session_state.feature_columns = feature_columns
            st.session_state.encoder_labels = encoder.categories_[0].tolist()

    st.subheader("Masukkan nilai untuk memprediksi harga parfum")
    if "model" in st.session_state and "feature_columns" in st.session_state:
        user_input = {}
        for col in st.session_state.feature_columns:
            user_input[col] = st.number_input(f"Masukkan nilai untuk {col}", value=0.0)

        label_input = st.selectbox("Pilih nilai label cluster:", st.session_state.encoder_labels)

        if st.button("Prediksi"):
            try:
                input_numerical = np.array([[user_input[col] for col in st.session_state.feature_columns]])
                label_encoded = st.session_state.encoder.transform([[label_input]])
                input_combined = np.hstack((input_numerical, label_encoded))
                input_scaled = st.session_state.scaler.transform(input_combined)

                prediction = st.session_state.model.predict(input_scaled)[0]
                st.success(f"Prediksi harga parfum: {prediction:.2f}")
            except Exception as e:
                st.error(f"Gagal melakukan prediksi: {e}")
    else:
        st.warning("Latih model terlebih dahulu sebelum melakukan prediksi.")
