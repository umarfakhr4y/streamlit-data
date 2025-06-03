import numpy as np
from sklearn.discriminant_analysis import StandardScaler
from sklearn.preprocessing import OneHotEncoder
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

    # Ambil semua nama tabel yang ada di database
    all_tables = inspector.get_table_names()
    clustering_tables = [t for t in all_tables if t.startswith("clustering_result_")]

    # selected_table = st.selectbox("Pilih tabel clustering dari Database", clustering_tables)
    uploaded_file = st.file_uploader("Unggah File CSV atau Excel dengan data harga parfum", type=["csv", "xlsx"])

    data = None
    # if selected_table:
    #     try:
    #         data = pd.read_sql_table(selected_table, con=engine)
    #         st.success(f"Data dari tabel '{selected_table}' berhasil dimuat.")
    #         st.dataframe(data)
    #     except Exception as e:
    #         st.error(f"Gagal memuat data dari tabel: {e}")
    #         return
    if uploaded_file:
        try:
            file_ext = uploaded_file.name.split(".")[-1]
            
            if file_ext == "csv":
                st.info("File CSV terdeteksi. Silakan pilih delimiter yang sesuai.")
                delimiter = st.selectbox(
                    "Pilih delimiter CSV:",
                    options={
                        ",": "Koma (,)",
                        ";": "Titik koma (;)",
                        "\t": "Tab (\\t)",
                        "|": "Pipa (|)"
                    },
                    format_func=lambda x: {
                        ",": "Koma (,)",
                        ";": "Titik koma (;)",
                        "\t": "Tab (\\t)",
                        "|": "Pipa (|)"
                    }[x],
                    index=1  # Default ke titik koma (;)
                )
                data = pd.read_csv(uploaded_file, sep=delimiter, on_bad_lines='skip')
            else:
                data = pd.read_excel(uploaded_file)       
            st.success("Data berhasil dimuat!")
            st.write("Tampilan data:")
            st.dataframe(data)
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memuat data: {e}")
            return

    if data is not None:
        st.subheader("Pilih kolom untuk digunakan dalam prediksi")
        feature_columns = st.multiselect("Pilih fitur (kolom numerik)", data.columns)
        target_column = st.selectbox("Pilih kolom target (Harga)", data.select_dtypes(include=["number"]).columns.tolist())

        if st.button("Latih Model"):
            if len(feature_columns) == 0 or target_column is None:
                st.error("Harap pilih kolom fitur dan target.")
                return

            X = data[feature_columns]
            y = data[target_column]

                # One-Hot Encoding untuk cluster
            encoder = OneHotEncoder(sparse_output=False, drop='first')
            # Hilangkan dummy pertama untuk menghindari multikolinearitas
            X_encoded = encoder.fit_transform(data[['Labels']])

            # Gabungkan dengan fitur lain
            X_final = np.hstack((data[['FORMULA', 'AQUADEST', 'ALKOHOL']].values, X_encoded))

            # Normalisasi fitur numerik
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_final)

            # Membagi data menjadi training dan testing
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

            # Model Regresi Linear
            model = LinearRegression()
            model.fit(X_train, y_train)

            # Memprediksi harga di data uji
            y_pred = model.predict(X_test)

            # Evaluasi model
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)


            st.write("Model dilatih dengan sukses!")
            st.write(f"Mean Squared Error: {mse}")
            st.write(f"R² Score: {r2}")

            st.session_state.model = model
            st.session_state.feature_columns = feature_columns

    st.subheader("Masukkan nilai untuk memprediksi harga parfum")
    if "model" in st.session_state and "feature_columns" in st.session_state:
        user_input = {}
        for col in st.session_state.feature_columns:
            user_input[col] = st.number_input(f"Masukkan nilai untuk {col}", value=0.0)
        
        if st.button("Prediksi"):
            input_data = pd.DataFrame([user_input])
            prediction = st.session_state.model.predict(input_data)[0]
            st.success(f"Prediksi harga parfum: {prediction:.2f}")
    else:
        st.warning("Latih model terlebih dahulu sebelum melakukan prediksi.")
