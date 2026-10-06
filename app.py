import streamlit as st
import pandas as pd
import datetime
import os

# Tetapan halaman web
st.set_page_config(
    page_title="Gold Trading Journal & Dashboard",
    page_icon="🪙",
    layout="wide"
)

# Nama fail tempat simpan data trade secara automatik
DATA_FILE = "trading_data.csv"

# Fungsi untuk muat turun data
@st.cache_data(experimental_allow_widgets=True)
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Data kosong permulaan jika belum ada trade
        return pd.DataFrame(columns=[
            "Tarikh", "Pair", "Jenis", "Lot", "Harga Masuk", "Harga Keluar", "Profit/Loss ($", "Nota"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

st.title("🪙 Gold (XAUUSD) Trading Journal & Dashboard")
st.markdown("---")

# Menu Navigasi (Sidebar)
menu = st.sidebar.selectbox("Navigasi Menu", ["📊 Dashboard", "📝 Masuk Trade Baru (Manual)", "📋 Senarai Journal"])

# ==================== 1. DASHBOARD ====================
if menu == "📊 Dashboard":
    st.subheader("Ringkasan Prestasi Trading")
    
    if df.empty:
        st.info("Belum ada data trade dimasukkan. Sila isi di menu **'Masuk Trade Baru'**.")
    else:
        # Kiraan metrik utama
        total_trades = len(df)
        total_pl = df["Profit/Loss ($"].sum()
        winning_trades = len(df[df["Profit/Loss ($"] > 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Paparan kad metrik
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Jumlah Trade", total_trades)
        col2.metric("Total Profit/Loss", f"${total_pl:.2f}", delta=f"${total_pl:.2f}")
        col3.metric("Win Rate", f"{win_rate:.1f}%")
        col4.metric("Jumlah Menang", f"{winning_trades} Trade")
        
        st.markdown("---")
        st.subheader("Graf Prestasi Terkini")
        if "Tarikh" in df.columns and not df.empty:
            df['Tarikh'] = pd.to_datetime(df['Tarikh'])
            df_sorted = df.sort_values("Tarikh")
            df_sorted['Kumulatif PL'] = df_sorted["Profit/Loss ($"].cumsum()
            st.line_chart(df_sorted.set_index("Tarikh")["Kumulatif PL"])

# ==================== 2. MASUK TRADE BARU ====================
elif menu == "📝 Masuk Trade Baru (Manual)":
    st.subheader("Borang Masuk Trade Manual")
    
    with st.form("trade_form"):
        col1, col2 = st.columns(2)
        with col1:
            tarikh = st.date_input("Tarikh Trade", datetime.date.today())
            pair = st.selectbox("Pair", ["XAUUSD", "EURUSD", "GBPUSD", "Lain-lain"])
            jenis = st.selectbox("Jenis Order", ["BUY", "SELL"])
            lot = st.number_input("Saiz Lot", min_value=0.01, value=0.10, step=0.01)
            
        with col2:
            harga_masuk = st.number_input("Harga Masuk (Entry)", value=2000.00, step=0.1)
            harga_keluar = st.number_input("Harga Keluar (Exit)", value=2010.00, step=0.1)
            profit_loss = st.number_input("Profit / Loss ($)", value=0.00, step=1.0)
            nota = st.text_area("Nota / Analisis Setup")
            
        submit_button = st.form_submit_button("Simpan Trade")
        
        if submit_button:
            new_data = pd.DataFrame([{
                "Tarikh": str(tarikh),
                "Pair": pair,
                "Jenis": jenis,
                "Lot": lot,
                "Harga Masuk": harga_masuk,
                "Harga Keluar": harga_keluar,
                "Profit/Loss ($": profit_loss,
                "Nota": nota
            }])
            
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df)
            st.success("Trade berjaya disimpan! Dashboard telah dikemas kini secara auto.")
            st.balloons()

# ==================== 3. SENARAI JOURNAL ====================
elif menu == "📋 Senarai Journal":
    st.subheader("Rekod Semua Trade")
    if df.empty:
        st.info("Tiada rekod trade lagi.")
    else:
        st.dataframe(df, use_container_width=True)
        
        if st.button("Padam Semua Data Rekod"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.experimental_rerun()
