import streamlit as st
import streamlit_option_menu as som
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kstest

#buat jadi wide
st.set_page_config(layout="wide")
# Sidebar navigation
with st.sidebar:
    st.write("**By: Di Asih I Maruddani**")
    selected = som.option_menu(
        'CAPM',
        ["Home", "Pilih Saham", "Analisis Return Saham", "Seleksi Saham", "Bobot Portofolio CAPM", "Value at Risk", "Kinerja Portofolio"],
        icons=['house', 'bar-chart', 'currency-exchange', 'check-circle', 'gear', 'exclamation-triangle', 'graph-up'],
        menu_icon="laptop",
        default_index=0,
        orientation="vertical",
        styles={
            "icon": {"font-size": "20px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "grey"},
        }
    )

# Home page
if selected == "Home":
    st.title("Home")
    st.write("Selamat datang di aplikasi CAPM untuk analisis dan optimisasi portofolio saham.")
    
    # Submenu for Home pagespo
    subhome = som.option_menu(
        "", 
        ["Tentang Web", "Cara Penggunaan Web"],
        icons=['info-circle', 'question-circle'],
        default_index=0,
        orientation="horizontal",
        styles={
            "icon": {"font-size": "15px"},
            "nav-link": {"font-size": "15px", "text-align": "mid", "margin":"0px", "--hover-color": "grey"},  
        }
    )

   # Content untuk "Tentang Web"
    if subhome == "Tentang Web":
        # Header
        st.subheader("📝 **Tentang Web**")
        
        # Konten Deskripsi
        st.markdown("""
        **Web CAPM** dirancang sebagai platform untuk membantu investor dalam 
        - **Menyeleksi saham** berdasarkan kriteria tertentu
        - **Menganalisis return saham** dan kinerja portofolio
        - **Mengoptimalkan portofolio** saham menggunakan **COMPLIANT ASSET PRICING MODEL (CAPM)**.  

        Dengan fitur-fitur canggih dan analisis berbasis data, web ini dapat membantu Anda membuat **keputusan investasi** yang lebih **tepat** dan **efisien**.
        """)
        
        # Highlight Box
        st.success("🔍 **Fokus utama web ini adalah membantu investor membentuk portofolio optimal tanpa harus melakukan skenario Short-Selling.**")

    # Content untuk "Cara Penggunaan Web"
    elif subhome == "Cara Penggunaan Web":
        # Header
        st.subheader("🛠️ **Cara Penggunaan Web**")
        
        # Panduan Langkah-langkah
        st.write("""
        Ikuti langkah-langkah berikut untuk memanfaatkan fitur MSV-QP:

        1. **📥 Pilih Saham**:  
            - Masukkan kode saham atau **unggah file CSV** yang berisi data saham.  
        2. **📊 Analisis Return Saham**:  
            - Lakukan analisis **return** saham-saham yang telah dipilih, mulai dari nilai return, plot return, dan analisis statistik deskriptif return.  
        3. **✅ Seleksi Saham**:  
            - Pilih saham berdasarkan **rata-rata return** dan **korelasi antar saham**. Atau masukkan jumlah saham yang akan dijadikan portofolio.  
        4. **⚙️ Mean-Semivariance QP Optimization**:  
            - Pada Tab ini, lakukan perhitungan bobot portofolio optimal berdasarkan hasil rekomendasi sistem, atau pilih saham lain sesuai dengan preferensi investor dengan melakukan input kode saham.  
        5. **📉 Value at Risk (VaR)**:  
            - Hitung potensi **kerugian maksimum** portofolio menggunakan metode **Historical Simulation**.  
        6. **🏆 Evaluasi Kinerja Portofolio**:  
            - Gunakan **Indeks Sharpe** untuk menilai performa portofolio berdasarkan return dan risiko.  
        """)


# Pilih Saham page
elif selected == "Pilih Saham":
    st.title("Pilih Saham")
    st.write("Masukkan kode saham yang ingin Anda analisis atau unggah file CSV.")

    # Input saham secara manual
    if 'saham_input' not in st.session_state:
        st.session_state['saham_input'] = ""

    saham_input = st.text_input("Masukkan kode saham (pisahkan dengan koma untuk lebih dari satu, misal: BBCA.JK, ADRO.JK, JSMR.JK, dst):", value=st.session_state['saham_input'])
    
    # Input rentang tanggal
    start_date = st.date_input('Tanggal awal', pd.to_datetime("2021-01-11"))
    end_date = st.date_input('Tanggal akhir', pd.to_datetime("today"))

    st.session_state['start_date'] = start_date
    st.session_state['end_date'] = end_date

    # unduh data IHSG dari Yahoo Finance untuk benchmark
    start_date = st.session_state['start_date']
    end_date = st.session_state['end_date']
    IHSG = yf.download("^JKSE", start=start_date, end=end_date)['Close']
    IHSG.index = IHSG.index.normalize()
    IHSG.index = IHSG.index.strftime('%Y-%m-%d')
    return_IHSG = np.log(IHSG / IHSG.shift(1))
    st.session_state['return_IHSG'] = return_IHSG 

 
    # Mengambil data saham dari Yahoo Finance 
    if saham_input: 
        saham_list = [s.strip().upper() for s in saham_input.split(',')] 
        st.session_state['saham_list'] = saham_list 
         
        try: 
            data = yf.download(saham_list, start=start_date, end=end_date)['Close'] 
            data.index = data.index.normalize() 
            data.index = data.index.strftime('%Y-%m-%d') 
            st.session_state['data'] = data 
            st.write("Data Saham yang dipilih:") 
            st.dataframe(data) 
        except Exception as e: 
            st.error(f"Terjadi kesalahan dalam pengambilan data saham: {e}") 
        st.session_state['saham_input'] = saham_input 
    # Unggah data CSV 
    uploaded_file = st.file_uploader("Atau upload file CSV", type=["csv"]) 
    if uploaded_file: 
        try: 
            data = pd.read_csv(uploaded_file, parse_dates=['Date'], index_col='Date') 
            data.index = data.index.normalize() 
            data.index = data.index.strftime('%Y-%m-%d') 
            st.session_state['data'] = data 
            st.write("Data dari file CSV:")
            st.dataframe(data)
        except Exception as e:
            st.error(f"Terjadi kesalahan dalam memproses file CSV: {e}")

# Return Saham page
elif selected == "Analisis Return Saham":
    subreturn = som.option_menu(
        "Analisis Return Saham",  
        ["Return Saham", "Plot Return", "Statistics Descriptive","Uji Normalitas"], 
        default_index=0, 
        orientation="horizontal",
        styles={ 
            "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "grey"},
        }
    )
    
    if subreturn == "Return Saham":
        st.title("Return Saham")
        
        if 'data' in st.session_state:
            data = st.session_state['data']
            
            # Menghitung return saham logaritmik
            return_saham = np.log(data / data.shift(1))
            
            # Simpan return saham ke session state
            st.session_state['return_saham'] = return_saham
            st.session_state['return_saham1'] = return_saham
            
            st.write("Return Saham:")
            st.dataframe(return_saham)
        
        else:
            st.warning("Silakan pilih saham terlebih dahulu di halaman 'Pilih Saham'.")


    elif subreturn == "Plot Return":
        st.title("Plot Return Saham")
        sns.set(style="whitegrid")
        # Pastikan 'return_saham' adalah DataFrame
        if 'return_saham' in st.session_state and isinstance(st.session_state['return_saham'], pd.DataFrame):
            # Memilih saham untuk diplot
            return_plot = st.selectbox("Pilih saham untuk diplot:", st.session_state['return_saham'].columns, index=0)

            if return_plot in st.session_state['return_saham'].columns:
                fig, ax = plt.subplots(figsize=(15, 7))
                st.session_state['return_saham'][return_plot].plot(ax=ax)
                ax.set_title(f"Return Saham {return_plot}")
                ax.set_xlabel("Tanggal")
                ax.set_ylabel("Return")
                st.pyplot(fig)
            else:
                st.warning("Saham yang dipilih tidak ada dalam data return.")
        else:
            st.warning("Silakan pilih saham terlebih dahulu di halaman 'Pilih Saham'.")

    elif subreturn == "Statistics Descriptive":
        st.title("Statistics Descriptive")
        
        # Pastikan 'return_saham' adalah DataFrame
        if 'return_saham' in st.session_state and isinstance(st.session_state['return_saham'], pd.DataFrame):
            return_saham = st.session_state['return_saham']
            statdesc_summary = return_saham.describe()
            st.session_state['statdesc_summary'] = statdesc_summary
            st.write("Statistics Descriptive Return Saham:")
            st.dataframe(statdesc_summary)
        else:
            st.warning("Silakan pilih saham terlebih dahulu di halaman 'Pilih Saham'.")

    elif subreturn == "Uji Normalitas":
        st.title("Uji Normalitas")
        st.write("Uji Normalitas Univariat Menggunakan Kolmogorov-Smirnov Test.")
        
        # Ambil return saham dari session state
        if 'return_saham' in st.session_state and isinstance(st.session_state['return_saham'], pd.DataFrame):
            return_saham = st.session_state['return_saham']
            
            # Hapus baris yang mengandung NaN agar KS-Test tidak error
            return_saham_clean = return_saham.dropna()

            # Pastikan hanya kolom numerik yang diuji
            numeric_data = return_saham_clean.select_dtypes(include='number')

            if numeric_data.empty:
                st.error("❌ Data tidak mengandung kolom numerik. Silakan periksa data Anda.")
            else:
                # Standarisasi data agar mean = 0 dan std = 1 sebelum KS-Test
                standardized_data = numeric_data.apply(lambda x: (x - x.mean()) / x.std(), axis=0)

                # Lakukan KS-Test untuk setiap kolom
                ks_results = {col: kstest(standardized_data[col], 'norm') for col in standardized_data.columns}

                # Konversi hasil KS-Test ke DataFrame
                ks_results_df = pd.DataFrame(ks_results, index=['KS Statistic', 'p-value']).T

                # Interpretasi hasil KS-Test
                ks_results_df['Kesimpulan'] = ks_results_df['p-value'].apply(
                    lambda p: "❌ Return Tidak Berdistribusi Normal" if p < 0.05 else "✅ Return Berdistribusi Normal"
                )

                # Tambahkan pewarnaan pada tabel
                def highlight_interpretasi(val):
                    color = 'red' if "❌ Return Tidak Berdistribusi Normal" in val else 'green'
                    return f'color: {color}; font-weight: bold'

                styled_ks_df = ks_results_df.style.applymap(highlight_interpretasi, subset=['Kesimpulan'])

                # Layout dengan kolom agar lebih rapi
                col1, col2 = st.columns(2)

                with col1:
                    st.write("### 📊 Hasil Uji Normalitas")
                    st.dataframe(styled_ks_df, use_container_width=True)

                with col2:
                    st.write("### 📈 Distribusi Data")
                    selected_stock = st.selectbox("Pilih saham untuk melihat distribusi", numeric_data.columns)
                    fig, ax = plt.subplots(figsize=(6, 4))
                    sns.histplot(standardized_data[selected_stock], kde=True, bins=20, ax=ax, color="royalblue")
                    ax.set_title(f"Distribusi {selected_stock}")
                    ax.set_xlabel("Nilai Standarisasi")
                    ax.set_ylabel("Frekuensi")
                    st.pyplot(fig)
                
                st.error("Saham yang tidak berdistribusi normal tidak akan dimasukkan ke dalam optimasi portofolio.")
                #drop saham yang tidak berdistribusi normal
                return_saham_normal = ks_results_df[ks_results_df['Kesimpulan'] == "✅ Return Berdistribusi Normal"].index
                st.session_state['return_saham_normal'] = return_saham_normal

        else:
            st.warning("Silakan pilih saham terlebih dahulu di halaman 'Pilih Saham'.")


# Seleksi Saham Page
elif selected == "Seleksi Saham":
    st.title("Seleksi Saham")
    st.write("Pilih saham berdasarkan return dan korelasi.")

    subseleksi = som.option_menu(
        "Seleksi Saham", 
        ["Rata-rata return", "Korelasi", "Rekomendasi Kombinasi Saham"], 
        default_index=0, 
        orientation="horizontal",
        menu_icon="check-circle",
        styles={ 
            "nav-link": {"font-size": "15px", "text-align": "mid", "margin":"0px", "--hover-color": "grey"},
        }
    )

    if subseleksi == "Rata-rata return":
            st.title("Rata-rata return")
            # Pastikan 'return_saham' adalah DataFrame
            #hanya hitung mean return saham yang berdistribusi normal
            if 'return_saham' in st.session_state and isinstance(st.session_state['return_saham'], pd.DataFrame):
                return_saham = st.session_state['return_saham']
                return_saham_normal = st.session_state['return_saham_normal']
                return_saham = return_saham[return_saham_normal]
                # Hitung rata-rata return
                mean_values = return_saham.mean()
                statdesc_summary = mean_values.sort_values(ascending=False).to_frame(name="Mean")
                st.session_state['statdesc_summary'] = statdesc_summary
                st.write("Rata-rata return setiap saham yang memenuhi asumsi normalitas:")
                st.dataframe(statdesc_summary)

            else:
                st.warning("Silakan pilih saham terlebih dahulu di halaman 'Pilih Saham'.")

    elif subseleksi == "Korelasi":
        st.title("Korelasi")
        # Pastikan 'return_saham' adalah DataFrame
        if 'return_saham' in st.session_state and isinstance(st.session_state['return_saham'], pd.DataFrame):
            return_saham = st.session_state['return_saham']
            return_saham_normal = st.session_state['return_saham_normal']
            return_saham = return_saham[return_saham_normal]
            # Hitung matriks korelasi
            corr_matrix = return_saham.corr()
            st.session_state['manual_correlation'] = corr_matrix
            st.write("Matriks Korelasi Return Saham:")
            plt.figure(figsize=(20, 10))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", cbar_kws={'label': 'Korelasi'})
            plt.title('Correlation Matrix')
            st.pyplot(plt.gcf())
            plt.clf()  # Clear plot setelah ditampilkan
        else:
            st.warning("Silakan pilih saham terlebih dahulu di halaman 'Pilih Saham'.")


    elif subseleksi == "Rekomendasi Kombinasi Saham":
        st.title("Rekomendasi Kombinasi Saham")

        # Input jumlah Rekomendasi Kombinasi Saham yang diinginkan
        if 'jumlah_kombinasi' not in st.session_state:
            st.session_state['jumlah_kombinasi'] = ""

        jumlah_kombinasi = st.text_input("Masukkan jumlah saham yang akan dijadikan portofolio (misalnya, 2 atau 3):", value=st.session_state['jumlah_kombinasi'])
        st.session_state['jumlah_kombinasi'] = jumlah_kombinasi

        # Cek apakah input jumlah kombinasi adalah angka dan konversi ke integer
        try:
            jumlah_kombinasi = int(jumlah_kombinasi)
        except ValueError:
            st.warning("Masukkan angka yang valid untuk jumlah kombinasi.")
            jumlah_kombinasi = None

        # Pastikan statdesc_summary dan manual_correlation tersedia di session state
        if 'statdesc_summary' in st.session_state and 'manual_correlation' in st.session_state and jumlah_kombinasi:

            statdesc_summary = st.session_state['statdesc_summary']
            manual_correlation = st.session_state['manual_correlation']

            # Hanya pilih saham dengan rata-rata return positif
            statdesc_summary_positive = statdesc_summary[statdesc_summary['Mean'] > 0]

            # Dapatkan 10 besar saham berdasarkan rata-rata return positif
            top20_return_saham = statdesc_summary_positive.sort_values(by='Mean', ascending=False).head(20)

            # Ambil saham pertama berdasarkan return tertinggi
            selected_stocks = [top20_return_saham.index[0]]
            st.success(f"Saham ke-1: {selected_stocks[0]}")

            # Ambang batas korelasi
            threshold = 0.1999 #korelasi sangat rendah  

            # Pemilihan saham tambahan hingga mencapai jumlah kombinasi yang diinginkan
            while len(selected_stocks) < jumlah_kombinasi:
                calon_saham = top20_return_saham.index.difference(selected_stocks)

                # Filter saham yang memiliki korelasi rendah terhadap semua saham yang sudah terpilih
                valid_candidates = []
                for saham in calon_saham:
                    if all(abs(manual_correlation.loc[saham, selected]) <= threshold for selected in selected_stocks):
                        valid_candidates.append(saham)

                if valid_candidates:
                    # Pilih saham berikutnya dari kandidat dengan return tertinggi yang valid
                    next_saham = valid_candidates[0]
                    selected_stocks.append(next_saham)
                    st.success(f"Saham ke-{len(selected_stocks)}: {next_saham}")
                else:
                    st.warning("Tidak ada saham lain yang memenuhi kriteria expected return tinggi dengan korelasi rendah.")
                    break  # Hentikan jika tidak ada kandidat yang memenuhi kriteria

            # simpan saham yang dipilih di session state
            st.session_state['selected_stocks'] = selected_stocks

        else:
            st.warning("Silakan pilih saham terlebih dahulu di halaman 'Pilih Saham'.")



# Bobot Portofolio CAPM page
elif selected == "Bobot Portofolio CAPM":
    st.title("Bobot Portofolio CAPM")
    st.write("Optimisasi bobot portofolio menggunakan metode Compliant Asset Pricing Model (CAPM).")

    # Pilihan menu untuk memilih saham
    submsv = som.option_menu(
        "",
        ["Bobot Saham Rekomendasi", "Pilih Saham Manual"],
        default_index=0,
        orientation="horizontal",
        styles={
            "nav-link": {"font-size": "15px", "text-align": "mid", "margin": "0px", "--hover-color": "grey"},
        }
    )
    
    # Input suku bunga acuan
    BI_rate = st.number_input("Masukkan suku bunga acuan (BI rate) dalam persen:", value=6.0)
    rf= (BI_rate/100)/365

    # Jika pilihan sesuai pada hasil bagian Rekomendasi Kombinasi Saham
    if submsv == "Bobot Saham Rekomendasi":
        st.write("Anda memilih opsi saham yang direkomendasikan.")

        # Pastikan state untuk selected_stocks ada
        if 'selected_stocks' not in st.session_state:
            st.session_state['selected_stocks'] = ""
        saham_list_com = st.session_state['selected_stocks']

        # Pastikan state untuk return_saham1 ada
        if 'return_saham1' not in st.session_state:
            st.session_state['return_saham1'] = ""
        return_saham1 = st.session_state['return_saham1']

        # Pastikan state untuk return IHSG juga ada
        return_IHSG = st.session_state['return_IHSG']
        
        # Tombol untuk memulai perhitungan optimasi
        if st.button("Lakukan Optimasi"):
            # Filter data saham yang dipilih
            selected_return_saham = return_saham1[saham_list_com]

            # Buat DataFrame baru (copy data saham yang dipilih)
            new_data = selected_return_saham.copy()
            new_data['IHSG'] = return_IHSG

            #simpen yang baru ke session state
            st.session_state['new_data_ada_IHSG'] = new_data

            # Menghitung varian covarian dataframe
            variance_results = new_data.var()
            covariance_results = new_data.cov()

            #ambil nilai varian ihsg dari varian_result
            variance_IHSG = variance_results['IHSG']

            #beta saham (covarian saham IHSG/varian IHSG)
            covariance_IHSG_result = covariance_results['IHSG']
            #drop IHSG
            beta_saham = covariance_IHSG_result / variance_IHSG
            beta_saham = beta_saham.drop('IHSG')

            # Menghitung beta portofolio (penjumlahan beta saham yang dipilih)
            beta_portofolio = beta_saham.sum()

            # Simpan hasil varian kovarian ke session state
            st.session_state['variance_results'] = variance_results
            st.session_state['variance_IHSG'] = variance_IHSG
            st.session_state['covariance_results'] = covariance_results
            st.session_state['covariance_IHSG_result'] = covariance_IHSG_result
            st.session_state['beta_saham'] = beta_saham
            st.session_state['beta_portofolio'] = beta_portofolio

            # Membuat matriks variance-covariance tanpa IHSG
            matrix_size = len(new_data.drop('IHSG', axis=1).columns)
            matrix_varcovar = np.zeros((matrix_size, matrix_size))

            # Masukkan varian di diagonal dan kovarian di luar diagonal
            for i in range(matrix_size):
                matrix_varcovar[i, i] = variance_results[new_data.drop('IHSG', axis=1).columns[i]]
                for j in range(i + 1, matrix_size):
                    matrix_varcovar[i, j] = covariance_results[new_data.drop('IHSG', axis=1).columns[i]][new_data.drop('IHSG', axis=1).columns[j]]
                    matrix_varcovar[j, i] = covariance_results[new_data.drop('IHSG', axis=1).columns[i]][new_data.drop('IHSG', axis=1).columns[j]]  #simetris 

            # Konversi ke matriks
            matrix_varcovar = np.matrix(matrix_varcovar)
            #inverse matrix varcovar
            matrix_varcovar_inv = np.linalg.inv(matrix_varcovar)

            # expected return tiap saham dengan rumus rf + beta saham * (return IHSG - rf)
            mean_IHSG= new_data['IHSG'].mean()
            E_return_CAPM = rf + beta_saham * (mean_IHSG - rf)
            
            #buat matrix baris yang berisi E_return_CAPM - Rf
            E_return_CAPM_rf = np.array(E_return_CAPM - rf)

            #transpose matrix E_return_CAPM_bar
            E_return_CAPM_rf_T = E_return_CAPM_rf.T

            #matriks satuan dengan ukuran 1 x matrix_size
            A = np.ones((1, matrix_size))

            #inverse matrix varcovar * E_return_CAPM_bar
            sigma_invers_kali_return = matrix_varcovar_inv @ E_return_CAPM_rf

            #optimal weight * A
            calon_bobot = A @ matrix_varcovar_inv @ E_return_CAPM_rf
            #bobot tiap saham (semua saham pada sigma_invers_kali_return/calob_bobot)
            bobot_saham_com = sigma_invers_kali_return / calon_bobot
            bobot_saham_com = np.array(bobot_saham_com).flatten()

            
            #simpan bobot saham ke session state
            bobot_saham_com_dict = dict(zip(saham_list_com, bobot_saham_com))
            st.session_state['bobot_saham_com'] = bobot_saham_com_dict

            # Tampilkan bobot saham
            st.write("Berikut adalah bobot tiap saham yang anda pilih:")
            col_count = len(bobot_saham_com) if len(bobot_saham_com) < 4 else 4  # Jumlah kolom maksimal 4
            cols = st.columns(col_count)

            for i, bobot in enumerate(bobot_saham_com):
                with cols[i % col_count]:  # Buat grid layout
                    st.metric(label=f"Saham {saham_list_com[i]}", value=f"{float(bobot)*100:.4f}%", delta=None)    
        else:
            st.warning("Silakan pilih opsi yang valid.")
       
    # Pilih saham yang anda inginkan untuk dijadikan portofolio
    elif submsv == "Pilih Saham Manual":
        
        if 'return_saham1' not in st.session_state:
            st.session_state['return_saham1'] = ""    
         
        return_saham1 = st.session_state['return_saham1']
        return_saham_normal = st.session_state['return_saham_normal']
        return_saham1= return_saham1[return_saham_normal]

        if 'return_IHSG' not in st.session_state:
            st.session_state['return_IHSG'] = ""
        
        return_IHSG = st.session_state['return_IHSG']  # Pastikan return IHSG juga ada di session state
        
        if 'pilih_saham_manual' not in st.session_state:
            st.session_state['pilih_saham_manual'] = ""
        
        pilihan_saham_manual = st.text_input("Masukkan Saham Pilihan Anda (pisahkan dengan koma untuk lebih dari satu, misal: BBCA, ADRO, JSMR, dst):", value=st.session_state['pilih_saham_manual'])
        st.session_state['pilih_saham_manual'] = pilihan_saham_manual

        if st.button("Lakukan Optimasi") and pilihan_saham_manual:
            
            # Ambil saham yang dimasukkan oleh pengguna
            saham_list_manual = [s.strip().upper() for s in pilihan_saham_manual.split(',')]
            
            # Pisahkan saham yang ada dan tidak ada dalam return_saham_normal
            saham_valid = [s for s in saham_list_manual if s in return_saham_normal]
            st.session_state['saham_valid'] = saham_valid
            saham_tidak_valid = [s for s in saham_list_manual if s not in return_saham_normal]
            st.session_state['saham_tidak_valid'] = saham_tidak_valid

            # Tampilkan peringatan jika ada saham yang tidak valid
            if saham_tidak_valid:
                st.warning(f"⚠️ Saham {', '.join(saham_tidak_valid)} tidak berdistribusi normal, **sehingga tidak akan dimasukkan ke dalam optimasi portofolio**")

            # Jika tidak ada saham yang valid, hentikan eksekusi
            if not saham_valid:
                st.error("Tidak ada saham yang bisa dioptimasi karena semuanya tidak berdistribusi normal.")
                st.stop()

            # Filter return_saham untuk hanya menyertakan saham yang ada di saham_list_manual
            selected_return_saham = return_saham1[saham_valid]

            # Buat DataFrame baru (copy data saham yang dipilih)
            new_data = selected_return_saham.copy()
            new_data['IHSG'] = return_IHSG

            # Simpan yang baru ke session state
            st.session_state['new_data_ada_IHSG'] = new_data

            # Menghitung varian covarian dataframe
            variance_results = new_data.var()
            covariance_results = new_data.cov()

            # Ambil nilai varian IHSG
            variance_IHSG = variance_results['IHSG']

            # Beta saham (kovarian saham IHSG/varian IHSG)
            covariance_IHSG_result = covariance_results['IHSG']
            beta_saham = covariance_IHSG_result / variance_IHSG
            beta_saham = beta_saham.drop('IHSG')

            # Menghitung beta portofolio (penjumlahan beta saham yang dipilih)
            beta_portofolio = beta_saham.sum()

            # Simpan hasil varian kovarian ke session state
            st.session_state['variance_results'] = variance_results
            st.session_state['variance_IHSG'] = variance_IHSG
            st.session_state['covariance_results'] = covariance_results
            st.session_state['covariance_IHSG_result'] = covariance_IHSG_result
            st.session_state['beta_saham'] = beta_saham
            st.session_state['beta_portofolio'] = beta_portofolio

            # Membuat matriks variance-covariance tanpa IHSG
            matrix_size = len(new_data.drop('IHSG', axis=1).columns)
            matrix_varcovar = np.zeros((matrix_size, matrix_size))

            # Masukkan varian di diagonal dan kovarian di luar diagonal
            for i in range(matrix_size):
                matrix_varcovar[i, i] = variance_results[new_data.drop('IHSG', axis=1).columns[i]]
                for j in range(i + 1, matrix_size):
                    matrix_varcovar[i, j] = covariance_results[new_data.drop('IHSG', axis=1).columns[i]][new_data.drop('IHSG', axis=1).columns[j]]
                    matrix_varcovar[j, i] = covariance_results[new_data.drop('IHSG', axis=1).columns[i]][new_data.drop('IHSG', axis=1).columns[j]]  # simetris

            # Konversi ke matriks
            matrix_varcovar = np.matrix(matrix_varcovar)
            # Inverse matrix varcovar
            matrix_varcovar_inv = np.linalg.inv(matrix_varcovar)

            # Expected return tiap saham dengan rumus rf + beta saham * (return IHSG - rf)
            mean_IHSG = new_data['IHSG'].mean()
            E_return_CAPM = rf + beta_saham * (mean_IHSG - rf)
            
            # Buat matrix baris yang berisi E_return_CAPM - rf
            E_return_CAPM_rf = np.array(E_return_CAPM - rf)

            # Transpose matrix E_return_CAPM_rf
            E_return_CAPM_rf_T = E_return_CAPM_rf.T

            # Matriks satuan dengan ukuran 1 x matrix_size
            A = np.ones((1, matrix_size))

            # Inverse matrix varcovar * E_return_CAPM_rf
            sigma_invers_kali_return = matrix_varcovar_inv @ E_return_CAPM_rf

            # Optimal weight * A
            calon_bobot = A @ matrix_varcovar_inv @ E_return_CAPM_rf
            # Bobot tiap saham
            bobot_saham_manual = sigma_invers_kali_return / calon_bobot
            bobot_saham_manual = np.array(bobot_saham_manual).flatten()

            # Simpan bobot saham ke session state
            st.session_state['bobot_saham_manual'] = bobot_saham_manual
            bobot_saham_manual_dict = dict(zip(saham_list_manual, bobot_saham_manual))
            st.session_state['bobot_saham_manual'] = bobot_saham_manual_dict

            # Tampilkan bobot saham
            st.write("Berikut adalah bobot tiap saham yang anda pilih:")
            col_count = len(bobot_saham_manual) if len(bobot_saham_manual) < 4 else 4  # Jumlah kolom maksimal 4
            cols = st.columns(col_count)

            for i, bobot in enumerate(bobot_saham_manual):
                with cols[i % col_count]:  # Buat grid layout
                    st.metric(label=f"Saham {saham_list_manual[i]}", value=f"{float(bobot)*100:.2f}%", delta=None)
        else:
            st.warning("Silakan pilih opsi yang valid.")

# Value at Risk page
elif selected == "Value at Risk":
    st.title("Value at Risk")
    st.write("Analisis Value at Risk (VaR) dari portofolio menggunakan metode Historical-Simulation.")
    
    # Sub-menu untuk VaR
    subvar = som.option_menu(
        "",
        ['VaR Portofolio Saham Rekomendasi', 'VaR Portofolio Saham Manual'],
        default_index=0,
        orientation="horizontal",
        styles={
            "nav-link": {"font-size": "15px", "text-align": "mid", "margin": "0px", "--hover-color": "grey"},
        }
    )
    
    # Ambil data dari session state
    if 'return_saham' not in st.session_state:
        st.session_state['return_saham'] = ""        
    return_saham = st.session_state['return_saham']

    if 'saham_valid' not in st.session_state:
        st.session_state['saham_valid'] = ""
    saham_valid = st.session_state['saham_valid']
    
    
    # Tampilkan hasil VaR untuk "VaR Portofolio Saham Rekomendasi"
    if subvar == "VaR Portofolio Saham Rekomendasi":
        if 'selected_stocks' not in st.session_state:
            st.session_state['selected_stocks'] = ""

        if 'return_saham_com' not in st.session_state:
            st.session_state['return_saham_com'] = ""
        return_saham_com = st.session_state['return_saham_com']

        saham_list_com = st.session_state['selected_stocks']
        if 'bobot_saham_com' not in st.session_state or not isinstance(st.session_state['bobot_saham_com'], dict):
            st.session_state['bobot_saham_com'] = {}
        bobot_saham_com = st.session_state['bobot_saham_com']
                
        # Input pengguna sebelum tombol
        persentil = float(st.text_input("Masukkan persentil VaR yang diinginkan (misalnya, 0.05 untuk 5% VaR):", value=0.05))
        V0 = float(st.text_input("Masukkan Modal awal:", value=1000000))
        T = float(st.text_input("Masukkan Holding Periode (dalam hari):", value=1))

        # Tambahkan tombol untuk menghitung VaR
        if st.button("Hitung VaR Portofolio Saham Rekomendasi"):
            # Inisialisasi return portofolio dengan nilai 0
            return_portofolio_com = pd.Series(0, index=return_saham.index)

            # Iterasi melalui dictionary bobot
            for saham, bobot in bobot_saham_com.items():
                if saham in saham_list_com:  # key " saham " harus ada dalam saham_list
                    return_portofolio_com += bobot * return_saham[saham]

            st.session_state['return_portofolio_com'] = return_portofolio_com

            # Urutkan return portofolio
            short_return_portofolio_com = return_portofolio_com.sort_values()
            mean_com= return_portofolio_com.mean()

            # Hitung VaR
            if 'VaR' not in st.session_state:
                st.session_state['VaR'] = ""
            VaR_com= -V0 * short_return_portofolio_com.quantile(persentil) * (T ** 0.5)
            st.session_state['VaR_com'] = VaR_com

            # Tampilkan hasil
            saham_list_com = ', '.join(saham_list_com)

            st.write(f"### 📈 Hasil Perhitungan VaR Portofolio Saham Rekomendasi")

            st.write(f"**📋 Daftar Saham dalam Portofolio:** {saham_list_com}")
            st.write(f"**💰 Modal Awal:** Rp {V0:,.0f}")
            st.write(f"**⏳ Holding Periode:** {int(T)} hari")
            st.write(f"**📌 Tingkat Kepercayaan:** {100 - persentil * 100:.0f}%")
            st.write(f"**💡 Value at Risk (VaR):** Rp {VaR_com:,.2f}")
            st.success(
                f"Artinya, dengan modal awal sebesar **Rp {V0:,.0f}**, holding periode selama **{int(T)} hari**, "
                f"dan tingkat kepercayaan sebesar **{100 - persentil * 100:.0f}%**, "
                f"risiko kerugian maksimal yang mungkin dialami adalah sebesar **Rp{VaR_com:,.0f}**, atau sebesar **{(VaR_com/V0)*100:.3f}%** dari modal awal."
            )

           
    # Tampilkan hasil VaR untuk "VaR Portofolio Saham Manual"
    elif subvar == "VaR Portofolio Saham Manual":
        if 'return_saham' not in st.session_state:
            st.session_state['return_saham'] = ""
        return_saham = st.session_state['return_saham']
        if 'pilih_saham_manual' not in st.session_state:
            st.session_state['pilih_saham_manual'] = ""  # Pastikan tidak error jika belum ada key
        if 'saham_valid' not in st.session_state:
            st.session_state['saham_valid'] = []  # Gunakan list kosong jika belum ada
        
        # Ambil daftar saham yang valid
        saham_valid = st.session_state['saham_valid']
        
        # Ambil daftar saham yang dipilih secara manual oleh user
        saham_list_manual = [s.strip().upper() for s in st.session_state['pilih_saham_manual'].split(',')]
        
        # Filter hanya saham yang valid
        saham_valid_manual = [s for s in saham_list_manual if s in saham_valid]

        if not saham_valid_manual:
            st.write("Saham valid dalam session_state:", st.session_state.get("saham_valid", []))
            st.error("Tidak ada saham valid yang bisa dihitung VaR-nya.")
            st.stop()

        # Pastikan bobot saham ada dalam session state
        if 'bobot_saham_manual' not in st.session_state or not isinstance(st.session_state['bobot_saham_manual'], dict):
            st.session_state['bobot_saham_manual'] = {}  # Gunakan dictionary kosong jika tidak ada
        
        bobot_saham_manual = st.session_state['bobot_saham_manual']

        # Input pengguna sebelum tombol
        persentil = float(st.text_input("Masukkan persentil VaR yang diinginkan (misalnya, 0.05 untuk 5% VaR):", value=0.05))
        V0 = float(st.text_input("Masukkan Modal awal:", value=1000000))
        T = float(st.text_input("Masukkan Holding Periode (dalam hari):", value=1))

        # Tambahkan tombol untuk menghitung VaR
        if st.button("Hitung VaR Portofolio Saham Manual"):

            # Inisialisasi return portofolio dengan nilai 0
            return_portofolio_man = pd.Series(0, index=st.session_state['return_saham'].index)

            # Iterasi hanya untuk saham valid
            for saham in saham_valid_manual:
                if saham in bobot_saham_manual:
                    return_portofolio_man += bobot_saham_manual[saham] * st.session_state['return_saham'][saham]

            # Simpan return portofolio ke session state
            st.session_state['return_portofolio_man'] = return_portofolio_man
            
            # Urutkan return portofolio
            short_return_portofolio_man = return_portofolio_man.sort_values()        

            # Hitung VaR
            VaR_man = -V0 * short_return_portofolio_man.quantile(persentil) * (T ** 0.5)
            st.session_state['VaR_man'] = VaR_man
            
            # Tampilkan hasil saham valid yang dihitung
            saham_valid_manual_str = ', '.join(saham_valid_manual)

            st.write(f"### 📈 Hasil Perhitungan VaR Portofolio Saham Manual")
            st.write(f"**📋 Daftar Saham dalam Portofolio:** {saham_valid_manual_str}")
            st.write(f"**💰 Modal Awal:** Rp {V0:,.0f}")
            st.write(f"**⏳ Holding Periode:** {int(T)} hari")
            st.write(f"**📌 Tingkat Kepercayaan:** {100 - persentil * 100:.0f}%")
            st.write(f"**💡 Value at Risk (VaR):** Rp {VaR_man:,.2f}")
            st.success(
                f"Artinya, dengan modal awal sebesar **Rp {V0:,.0f}**, holding periode selama **{int(T)} hari**, "
                f"dan tingkat kepercayaan sebesar **{100 - persentil * 100:.0f}%**, "
                f"risiko kerugian maksimal yang mungkin dialami adalah sebesar **Rp{VaR_man:,.0f}**, atau sebesar **{(VaR_man/V0)*100:.3f}%** dari modal awal."
            )
    else:
        st.warning("Silakan pilih opsi yang valid.")

# Kinerja Portofolio page
elif selected == "Kinerja Portofolio":
    st.title("Kinerja Portofolio")
    st.write("Analisis kinerja portofolio saham menggunakan Indeks Sharpe. Semakin tinggi nilai Indeks Sharpe, maka akan semakin baik kinerja portofolio.")
    subkinerja = som.option_menu(
        "",
        ['Saham Kombinasi', 'Saham Manual'],
        default_index=0,
        orientation="horizontal",
        styles={
            "nav-link": {"font-size": "15px", "text-align": "mid", "margin": "0px", "--hover-color": "grey"},
        }
    )

    if subkinerja == "Saham Kombinasi":
    # Pastikan 'return_portofolio_com' ada dalam session state dan berupa pd.Series
        if 'return_portofolio_com' not in st.session_state or not isinstance(st.session_state['return_portofolio_com'], pd.Series):
            st.session_state['return_portofolio_com'] = pd.Series()  # Inisialisasi sebagai pd.Series kosong
        return_portofolio_com = st.session_state['return_portofolio_com']
    
        # Hitung statistik
        std_return_portofolio_com = return_portofolio_com.std()
        mean_return_portofolio_com = return_portofolio_com.mean()
    
        # Input suku bunga acuan
        BI_rate = st.number_input("Masukkan suku bunga acuan (BI rate) dalam persen:", value=6.0)

    # Tombol untuk menghitung kinerja saham kombinasi
        if st.button("Hitung Kinerja Saham Kombinasi"):
            st.write("Kinerja Saham Kombinasi:")
            kinerja_portofolio_com = (mean_return_portofolio_com - (BI_rate / 100)/365) / std_return_portofolio_com
            st.success(f"Sharpe Ratio: {kinerja_portofolio_com:.4f}")

    elif subkinerja == "Saham Manual":
        # Pastikan 'return_portofolio_man' ada dalam session state dan berupa pd.Series
        if 'return_portofolio_man' not in st.session_state or not isinstance(st.session_state['return_portofolio_man'], pd.Series):
            st.session_state['return_portofolio_man'] = pd.Series()  # Inisialisasi sebagai pd.Series kosong
        return_portofolio_man = st.session_state['return_portofolio_man']
    
        # Hitung statistik
        std_return_portofolio_man = return_portofolio_man.std()
        mean_return_portofolio_man = return_portofolio_man.mean()
    
        # Input suku bunga acuan
        BI_rate = st.number_input("Masukkan suku bunga acuan (BI rate) dalam persen:", value=6.0)

        # Tombol untuk menghitung kinerja saham manual
        if st.button("Hitung Kinerja Saham Manual"):
            st.write("Kinerja Saham Manual:")
            kinerja_portofolio_man = (mean_return_portofolio_man - (BI_rate / 100)/365) / std_return_portofolio_man
            st.success(f"Sharpe Ratio: {kinerja_portofolio_man:.2f}")
    else:
        st.warning("Silakan pilih opsi yang valid.")
