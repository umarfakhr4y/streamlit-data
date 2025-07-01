import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from database import get_connection
from database import get_sqlalchemy_engine
from datetime import datetime
from sqlalchemy import inspect


def plot_with_legend(scatter_data, labels, selected_columns, is_pca=False):
    unique_labels = sorted(set(labels))
    cmap = plt.cm.get_cmap("viridis", len(unique_labels))
    
    plt.figure(figsize=(8, 6))
    for i in unique_labels:
        plt.scatter(
            scatter_data[labels == i, 0],
            scatter_data[labels == i, 1],
            label=f"Cluster {i}",
            s=50,
            c=[cmap(i)]
        )
    if is_pca:
        plt.xlabel("PC 1")
        plt.ylabel("PC 2")
        plt.title("Visualisasi Clustering dengan PCA (2D)")
    else:
        plt.xlabel(selected_columns[0])
        plt.ylabel(selected_columns[1])
        plt.title("Scatter Plot Clustering (2 Kolom)")

    plt.legend(title="Keterangan Warna")
    st.pyplot(plt)


def clustering_page():
    st.title("Data Clustering Parfum")
    
    uploaded_file = st.file_uploader("Unggah File CSV atau Excel", type=["csv", "xlsx"])
    
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame()

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
                st.session_state.data = pd.read_csv(uploaded_file, sep=delimiter, on_bad_lines='skip')
            
            elif file_ext in ["xls", "xlsx"]:
                st.session_state.data = pd.read_excel(uploaded_file)

            st.write(f"Jumlah baris: {st.session_state.data.shape[0]}, Jumlah kolom: {st.session_state.data.shape[1]}")
        except Exception as e:
            st.error(f"Gagal memuat data: {e}")

    if not st.session_state.data.empty:
        data = st.session_state.data

        st.subheader("Data Awal")
        st.dataframe(data)

        st.subheader("Pilih Kolom untuk Clustering")
        numeric_columns = data.select_dtypes(include=["number"]).columns.tolist()
        selected_columns = st.multiselect("Pilih Kolom Numerik:", numeric_columns)
        print(data)
        # return

        if selected_columns:
            clustering_data = data[selected_columns]
            st.write("Data yang Dipilih untuk Clustering:")
            st.dataframe(clustering_data)
            if st.button("Tampilkan Elbow Method (Optimal k)"):
                try:
                    scaler = StandardScaler()
                    scaled_data = scaler.fit_transform(clustering_data)

                    distortions = []
                    K = range(1, 11)

                    for k in K:
                        kmeans = KMeans(n_clusters=k, random_state=42)
                        kmeans.fit(scaled_data)
                        distortions.append(kmeans.inertia_)

                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.plot(K, distortions, marker='o')
                    ax.set_title("Elbow Method untuk Menentukan k Optimal")
                    ax.set_xlabel("Jumlah Cluster (k)")
                    ax.set_ylabel("Inertia")
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"Gagal menampilkan Elbow Method: {e}")


            scaler = StandardScaler()
            clustering_data_scaled = scaler.fit_transform(clustering_data)

            st.subheader("Pengaturan Clustering")
            num_clusters = st.slider("Pilih Jumlah Cluster (k):", min_value=2, max_value=10, value=3)

            if st.button("Jalankan Clustering"):
                try:
                    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
                    cluster_labels = kmeans.fit_predict(clustering_data_scaled)

                    st.session_state.data["Cluster"] = cluster_labels
                    st.success(f"Clustering selesai! Data telah dikelompokkan ke dalam {num_clusters} cluster.")
                    
                    st.subheader("Data dengan Label Cluster")
                    st.dataframe(st.session_state.data)

                    # Simpan hasil clustering agar bisa digunakan nanti
                    st.session_state.clustered_data = st.session_state.data.copy()


                    # Visualisasi Clustering
                    st.subheader("Visualisasi Hasil Clustering")
                    if len(selected_columns) == 2:
                        plt.figure(figsize=(8, 6))
                        plot_with_legend(clustering_data_scaled, cluster_labels, selected_columns)


                    elif len(selected_columns) == 3:
                        from mpl_toolkits.mplot3d import Axes3D
                        fig = plt.figure(figsize=(14, 8))  # Lebar ditambah jadi 14
                        ax = fig.add_subplot(111, projection='3d')
                        scatter = ax.scatter(
                            clustering_data_scaled[:, 0], clustering_data_scaled[:, 1], clustering_data_scaled[:, 2],
                            c=cluster_labels, cmap="viridis", s=60
                        )

                        ax.set_xlabel(selected_columns[0])
                        ax.set_ylabel(selected_columns[1])
                        ax.set_zlabel(selected_columns[2])
                        ax.set_title("Scatter Plot Clustering (3D)")

                        # Tambahkan legend manual berdasarkan warna
                        from matplotlib.lines import Line2D
                        import numpy as np

                        unique_labels = np.unique(cluster_labels)
                        cmap = plt.cm.get_cmap("viridis", len(unique_labels))
                        legend_elements = [
                            Line2D([0], [0], marker='o', color='w', label=f"Cluster {i}",
                                markerfacecolor=cmap(i), markersize=10)
                            for i in unique_labels
                        ]
                        ax.legend(handles=legend_elements, title="Keterangan Warna", loc='upper right')

                        plt.tight_layout()
                        st.pyplot(fig)


                    elif len(selected_columns) > 3:
                        st.warning("Dimensi terlalu tinggi untuk divisualisasikan langsung. Menggunakan PCA untuk pengurangan dimensi.")
                        
                        # PCA untuk reduksi dimensi
                        pca = PCA(n_components=2)
                        pca_data = pca.fit_transform(clustering_data_scaled)

                        plot_with_legend(pca_data, cluster_labels, selected_columns, is_pca=True)

                     # --- Evaluasi Clustering dengan Silhouette Score ---
                    from sklearn.metrics import silhouette_score, silhouette_samples

                    # Gunakan data hasil scaling dan cluster hasil KMeans
                    silhouette_avg = silhouette_score(clustering_data_scaled, cluster_labels)
                    st.subheader("Evaluasi Clustering - Silhouette Coefficient")
                    st.markdown(f"**Rata-rata Silhouette Coefficient:** `{silhouette_avg:.4f}`")

                    # Hitung nilai silhouette tiap data
                    silhouette_vals = silhouette_samples(clustering_data_scaled, cluster_labels)

                    # Tambahkan ke DataFrame
                    st.session_state.data["Silhouette"] = silhouette_vals
                    st.session_state.clustered_data = st.session_state.data.copy()  # Simpan termasuk silhouette

                    # Tampilkan rata-rata per cluster
                    silhouette_df = st.session_state.data.groupby("Cluster")["Silhouette"].mean().reset_index()
                    st.markdown("**Rata-rata Silhouette per Cluster:**")
                    st.dataframe(silhouette_df.style.format({"Silhouette": "{:.4f}"}))
                    
                except Exception as e:
                    st.error(f"Gagal melakukan clustering: {e}")



        st.subheader("Simpan Data dengan Label Cluster")
        if st.button("Simpan ke File CSV"):
            try:
                if "clustered_data" not in st.session_state:
                    st.warning("Data belum memiliki label cluster. Jalankan clustering terlebih dahulu.")
                else:
                    clustered_data = st.session_state.clustered_data
                    output_file = "clustered_data.csv"
                    clustered_data.to_csv(output_file, index=False, sep=',')
                    st.success(f"Data berhasil disimpan ke file '{output_file}'!")
                    
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="Unduh File CSV",
                            data=file,
                            file_name=output_file,
                            mime="text/csv"
                        )
            except Exception as e:
                st.error(f"Gagal menyimpan file: {e}")
                
        st.subheader("Simpan Data ke MySQL via XAMPP")
        if st.button("Simpan ke Database MySQL"):
            try:
                if "clustered_data" not in st.session_state:
                    st.warning("Data belum memiliki label cluster. Jalankan clustering terlebih dahulu.")
                else:
                    engine = get_sqlalchemy_engine()
                    clustered_data = st.session_state.clustered_data

                    if "Cluster" not in clustered_data.columns:
                        st.warning("Data belum memiliki label cluster. Jalankan clustering terlebih dahulu.")
                    else:
                        # Format tanggal
                        today = datetime.today().strftime('%Y_%m_%d')
                        base_table_name = f"clustering_result_{today}"

                        # Cek nama tabel yang sudah ada
                        inspector = inspect(engine)
                        existing_tables = inspector.get_table_names()

                        # Cari nomor unik yang belum digunakan
                        counter = 1
                        while f"{base_table_name}_{counter}" in existing_tables:
                            counter += 1

                        table_name = f"{base_table_name}_{counter}"

                        # Simpan ke MySQL
                        clustered_data.to_sql(table_name, con=engine, if_exists='replace', index=False)

                        st.success(f"Data berhasil disimpan ke database pada tabel '{table_name}'.")
            except Exception as e:
                st.error(f"Gagal menyimpan ke MySQL: {e}")
    


if __name__ == "__main__":
    clustering_page()
