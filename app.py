import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(
    page_title="Gold Trading Journal",
    page_icon="🪙",
    layout="wide"
)

DATA_FILE = "daily_trading_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Tarikh", "Sesi / Pair", "Jenis", "Lot", "Harga Masuk", "Harga Keluar", "Profit / Loss ($)", "Nota Harian"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

st.title("🪙 Gold (XAUUSD) Daily Trading Journal")
st.markdown("---")

menu = st.sidebar.selectbox("Menu", ["📊 Dashboard Ringkasan", "📝 Masuk Trade Harian", "📋 Rekod Harian"])

# 1. DASHBOARD
if menu == "📊 Dashboard Ringkasan":
    st.subheader("Dashboard Prestasi Harian")
    if df.empty:
        st.info("Belum ada data harian dimasukkan.")
    else:
        total_days = len(df)
        total_pl = df["Profit / Loss ($)"].sum()
        win_days = len(df[df["Profit / Loss ($)"] > 0])
        win_rate = (win_days / total_days) * 100 if total_days > 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Jumlah Hari Trade", total_days)
        c2.metric("Total P/L Keseluruhan", f"${total_pl:.2f}", delta=f"${total_pl:.2f}")
        c3.metric("Kadar Menang (Win Rate)", f"{win_rate:.1f}%")
        c4.metric("Hari Profit", f"{win_days} Hari")
        
        st.markdown("---")
        st.subheader("Graf Pertumbuhan P/L Harian")
        if not df.empty:
            df['Tarikh'] = pd.to_datetime(df['Tarikh'])
            df_sorted = df.sort_values("Tarikh")
            df_sorted['Kumulatif'] = df_sorted["Profit / Loss ($)"].cumsum()
            st.line_chart(df_sorted.set_index("Tarikh")['Kumulatif'])

# 2. MASUK TRADE HARIAN
elif menu == "📝 Masuk Trade Harian":
    st.subheader("Borang Rekod Harian")
    
    with st.form("daily_form"):
        col1, col2 = st.columns(2)
        with col1:
            tarikh = st.date_input("Tarikh", datetime.date.today())
            pair = st.text_input("Pair / Sesi", "XAUUSD (London/NY)")
            jenis = st.selectbox("Arah Utama", ["BUY", "SELL", "BOTH"])
            lot = st.number_input("Saiz Lot Purata", value=0.10, step=0.01)
        with col2:
            harga_masuk = st.number_input("Entry Utama", value=2000.00, step=0.1)
            harga_keluar = st.number_input("Exit Utama", value=2010.00, step=0.1)
            profit_loss = st.number_input("Net Profit / Loss untuk Hari Ini ($)", value=0.00, step=1.0)
            nota = st.text_area("Nota / Psikologi Trading Hari Ini")
            
        simpan = st.form_submit_button("Simpan Rekod Harian")
        
        if simpan:
            new_row = pd.DataFrame([{
                "Tarikh": str(tarikh),
                "Sesi / Pair": pair,
                "Jenis": jenis,
                "Lot": lot,
                "Harga Masuk": harga_masuk,
                "Harga Keluar": harga_keluar,
                "Profit / Loss ($)": profit_loss,
                "Nota Harian": nota
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("Rekod harian berjaya disimpan dan dikemas kini di dashboard!")
            st.balloons()

# 3. REKOD HARIAN
elif menu == "📋 Rekod Harian":
    st.subheader("Senarai Rekod Mengikut Hari")
    if df.empty:
        st.info("Tiada rekod lagi.")
    else:
        st.dataframe(df, use_container_width=True)
        if st.button("Padam Semua Data"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.rerun()
