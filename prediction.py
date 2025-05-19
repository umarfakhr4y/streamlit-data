import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def prediction_page():
    st.title("Prediksi Harga Parfum")

    # Upload dataset
    uploaded_file = st.file_uploader("Unggah File CSV atau Excel dengan data harga parfum", type=["csv", "xlsx"])
    
    # Dataset placeholder
    data = None
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                data = pd.read_csv(uploaded_file)
            else:
                data = pd.read_excel(uploaded_file)
            
            st.success("Data berhasil dimuat!")
            st.write("Tampilan data:")
            st.dataframe(data)
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memuat data: {e}")
            return

    # Pastikan dataset tersedia
    if data is not None:
        # Memilih kolom
        st.subheader("Pilih kolom untuk digunakan dalam prediksi")
        feature_columns = st.multiselect("Pilih fitur (kolom numerik)", data.select_dtypes(include=["number"]).columns.tolist())
        target_column = st.selectbox("Pilih kolom target (Harga)", data.columns)

        if st.button("Latih Model"):
            if len(feature_columns) == 0 or target_column is None:
                st.error("Harap pilih kolom fitur dan target.")
                return

            # Split data menjadi fitur dan target
            X = data[feature_columns]
            y = data[target_column]

            # Bagi data menjadi data latih dan uji
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Latih model regresi linear
            model = LinearRegression()
            model.fit(X_train, y_train)

            # Evaluasi model
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            st.write("Model dilatih dengan sukses!")
            st.write(f"Mean Squared Error: {mse:.2f}")
            st.write(f"R² Score: {r2:.2f}")

            # Simpan model di session state
            st.session_state.model = model
            st.session_state.feature_columns = feature_columns

    # Input untuk prediksi
    st.subheader("Masukkan nilai untuk memprediksi harga parfum")
    if "model" in st.session_state and "feature_columns" in st.session_state:
        user_input = {}
        for col in st.session_state.feature_columns:
            user_input[col] = st.number_input(f"Masukkan nilai untuk {col}", value=0.0)
        
        if st.button("Prediksi"):
            # Pastikan semua input tersedia
            input_data = pd.DataFrame([user_input])
            prediction = st.session_state.model.predict(input_data)[0]
            st.success(f"Prediksi harga parfum: {prediction:.2f}")
    else:
        st.warning("Latih model terlebih dahulu sebelum melakukan prediksi.")

# Jalankan fungsi jika script ini dijalankan
if __name__ == "__main__":
    prediction_page()
