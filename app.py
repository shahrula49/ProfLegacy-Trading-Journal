import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(
    page_title="Gold Trading Journal Oktober",
    page_icon="🪙",
    layout="wide"
)

DATA_FILE = "excel_style_journal.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Kosong permulaan mengikut kolum Excel anda
        return pd.DataFrame(columns=[
            "Hari", "Tarikh", "Deposit ($)", "Profit ($)", "Loss ($)", "Net P/L ($)", "Withdrawal ($)", "Balance ($)", "Notes"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

st.title("🪙 GOLD TRADING JOURNAL OKTOBER")
st.markdown("---")

menu = st.sidebar.selectbox("Menu", ["📊 Dashboard", "📝 Isi Rekod Harian", "📋 Paparan Jadual Excel"])

# 1. DASHBOARD
if menu == "📊 Dashboard":
    st.subheader("Ringkasan Prestasi Bulan Oktober")
    if df.empty:
        st.info("Belum ada data dimasukkan.")
    else:
        total_profit = df["Profit ($)"].sum()
        total_loss = df["Loss ($)"].sum()
        total_net_pl = df["Net P/L ($)"].sum()
        total_deposit = df["Deposit ($)"].sum()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Deposit", f"${total_deposit:.2f}")
        c2.metric("Total Profit", f"${total_profit:.2f}")
        c3.metric("Total Loss", f"${total_loss:.2f}")
        c4.metric("Net P/L Keseluruhan", f"${total_net_pl:.2f}", delta=f"${total_net_pl:.2f}")

# 2. ISI REKOD HARIAN
elif menu == "📝 Isi Rekod Harian":
    st.subheader("Borang Masuk Data Harian")
    
    with st.form("excel_form"):
        col1, col2 = st.columns(2)
        with col1:
            hari = st.number_input("Hari Ke- (Contoh: 1, 2, 3)", min_value=1, max_value=31, value=1)
            tarikh = st.date_input("Tarikh", datetime.date.today())
            deposit = st.number_input("Deposit ($)", value=0.00, step=10.0)
            profit = st.number_input("Profit ($)", value=0.00, step=10.0)
        with col2:
            loss = st.number_input("Loss ($)", value=0.00, step=10.0)
            withdrawal = st.number_input("Withdrawal ($)", value=0.00, step=10.0)
            balance = st.number_input("Balance Terkini ($)", value=0.00, step=10.0)
            notes = st.text_area("Notes / Catatan Harian")
            
        simpan = st.form_submit_button("Simpan Rekod")
        
        if simpan:
            # Kira Net P/L secara automatik (Profit - Loss)
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
            # Susun ikut hari
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
