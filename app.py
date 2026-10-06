import streamlit as st
import pandas as pd
import datetime
import os
from PIL import Image # Tambah import ni untuk load gambar

# --- FUNGSI PERSEDIAAN ---
st.set_page_config(
    page_title="ProfLegacy - Gold Trading Journal",
    layout="wide"
)

DATA_FILE = "proflegacy_journal.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Hari", "Tarikh", "Deposit ($)", "Profit ($)", "Loss ($)", 
            "Net P/L ($)", "Withdrawal ($)", "Balance ($)", "Notes"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# --- SIDEBAR DENGAN LOGO PROFLEGACY ---
# Anda perlu letakkan fail image_15.png (logo) dalam folder GitHub yang sama dengan app.py
try:
    logo_img = Image.open("image_15.png")
    st.sidebar.image(logo_img, width=250) # Letak logo di sidebar, saiz 250px
except FileNotFoundError:
    st.sidebar.error("Fail logo 'image_15.png' tidak dijumpai. Sila muat naik ke GitHub.")
    st.sidebar.title("ProfLegacy") # Fallback kalau gambar takde

st.sidebar.markdown("---")
menu = st.sidebar.selectbox("Menu", ["📊 Dashboard", "📝 Isi Rekod Harian", "📋 Paparan Jadual Excel"])

# --- DASHBOARD / REKOD UTAMA ---
# Tambah lambang carta emas dari imej di sebelah tajuk
st.title("📊 GOLD TRADING JOURNAL | ProfLegacy")
st.markdown("---")

# 1. DASHBOARD
if menu == "📊 Dashboard":
    st.subheader("Ringkasan Prestasi Bulan Ini")
    if df.empty:
        st.info("Belum ada data dimasukkan.")
    else:
        total_profit = df["Profit ($)"].sum()
        total_loss = df["Loss ($)"].sum()
        total_net_pl = df["Net P/L ($)"].sum()
        total_deposit = df["Deposit ($)"].sum()
        win_days = len(df[df["Profit ($)"] > 0])
        total_days = len(df)
        win_rate = (win_days / total_days) * 100 if total_days > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Deposit", f"${total_deposit:.2f}")
        c2.metric("Net P/L Keseluruhan", f"${total_net_pl:.2f}", delta=f"${total_net_pl:.2f}")
        c3.metric("Win Rate Harian", f"{win_rate:.1f}%")
        
        # Tambah Metrik Tambahan Kecil
        c4, c5, c6 = st.columns(3)
        c4.metric("Total Profit", f"${total_profit:.2f}", help="Jumlah hari untung sahaja")
        c5.metric("Total Loss", f"${total_loss:.2f}", help="Jumlah hari rugi sahaja")
        c6.metric("Hari Profit", f"{win_days} / {total_days} Hari")

# 2. ISI REKOD HARIAN
elif menu == "📝 Isi Rekod Harian":
    st.subheader("Borang Masuk Data Harian")
    
    with st.form("excel_form"):
        col1, col2 = st.columns(2)
        with col1:
            hari = st.number_input("Hari Ke-", min_value=1, max_value=31, value=1)
            tarikh = st.date_input("Tarikh", datetime.date.today())
            deposit = st.number_input("Deposit ($)", value=0.00, step=10.0, format="%.2f")
            profit = st.number_input("Profit ($)", value=0.00, step=10.0, format="%.2f")
        with col2:
            loss = st.number_input("Loss ($)", value=0.00, step=10.0, format="%.2f")
            withdrawal = st.number_input("Withdrawal ($)", value=0.00, step=10.0, format="%.2f")
            balance = st.number_input("Balance Terkini ($)", value=0.00, step=10.0, format="%.2f")
            notes = st.text_area("Notes / Catatan Harian")
            
        simpan = st.form_submit_button("Simpan Rekod")
        
        if simpan:
            net_pl = profit - loss
            
            new_row = pd.DataFrame([{
                "Hari": hari,
                "Tarikh": str(tarikh),
                "Deposit ($)": deposit,
                "Profit ($)": profit,
                "Loss ($)": loss,
                "Net P/L ($)": net_pl,
                "Withdrawal ($)": withdrawal,
                "Balance ($)": balance,
                "Notes": notes
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            df = df.sort_values(by="Hari").reset_index(drop=True)
            save_data(df)
            st.success("Rekod harian berjaya disimpan!")
            st.balloons()

# 3. PAPARAN JADUAL EXCEL
elif menu == "📋 Paparan Jadual Excel":
    st.subheader("Jadual Utama Journal")
    if df.empty:
        st.info("Tiada rekod lagi. Sila isi di menu **'Isi Rekod Harian'**.")
    else:
        st.dataframe(df, use_container_width=True)
        if st.button("Padam Semua Data"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.rerun()

# Footer Kecil
st.markdown("---")
st.markdown("##### ProfLegacy - Mastering Market Structure & Price Action Precision")
