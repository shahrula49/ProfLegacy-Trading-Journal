import streamlit as st
import pandas as pd
import datetime
import os
from PIL import Image
from io import BytesIO

# --- PENGHASILAN PDF REPORT (REPORTLAB) ---
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(
    page_title="ProfLegacy - Gold Trading Journal",
    layout="wide"
)

# --- CSS MODEN & KEMAS ---
def set_clean_style():
    css = """
    <style>
    @media (max-width: 768px) {
        .stMetric {
            background-color: #f8fafc;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_clean_style()

DATA_FILE = "proflegacy_journal_users.csv"
UPLOAD_DIR = "uploaded_screenshots"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def load_all_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if "Screenshot" not in df.columns:
            df["Screenshot"] = ""
        return df
    else:
        return pd.DataFrame(columns=[
            "Nama", "Hari", "Tarikh", "Deposit ($)", "Profit ($)", "Loss ($)", 
            "Net P/L ($)", "Withdrawal ($)", "Balance ($)", "Screenshot", "Notes"
        ])

def save_all_data(df):
    df.to_csv(DATA_FILE, index=False)

df_all = load_all_data()

# --- SIDEBAR: PILIH NAMA TRADER & NAVIGASI TERUS ---
try:
    logo_img = Image.open("image_15.png")
    st.sidebar.image(logo_img, width=220)
except FileNotFoundError:
    st.sidebar.title("ProfLegacy")

st.sidebar.markdown("---")
st.sidebar.subheader("Profil Trader")
trader_name = st.sidebar.text_input("Masukkan Nama Anda:", value="Trader 1").strip()

if not trader_name:
    trader_name = "Trader 1"

st.sidebar.markdown("---")
st.sidebar.subheader("Menu Navigasi Utama")

# "📚 Panduan & Kalendar Berita" diletakkan di barisan ATAS SEKALI
menu = st.sidebar.radio("Pilih Menu:", [
    "📚 Panduan & Kalendar Berita",
    "📊 Dashboard", 
    "📝 Isi Rekod Harian", 
    "📋 Paparan Jadual & Export PDF",
    "👥 Senarai Pengguna"
])

df_user = df_all[df_all["Nama"].str.lower() == trader_name.lower()] if not df_all.empty else pd.DataFrame(columns=df_all.columns)

st.title(f"📊 GOLD TRADING DASHBOARD | {trader_name.upper()}")
st.markdown("Sistem jurnal harian XAUUSD profesional, semakan screenshot trade history, kalendar ekonomi dinamik, dan eksport laporan.")
st.markdown("---")

# 1. PANDUAN & KALENDAR BERITA DINAMIK (MENU UTAMA DI ATAS)
if menu == "📚 Panduan & Kalendar Berita":
    st.subheader("📚 Panduan, Rujukan & Kalendar Berita Ekonomi Harian (XAUUSD)")
    st.markdown("Pilih tarikh di bawah untuk melihat jadual rujukan berita ekonomi bagi hari tersebut.")
    st.markdown("---")
    
    # Pemilih Tarikh Dinamik untuk Kalendar Berita
    selected_news_date = st.date_input("Pilih Tarikh Kalendar Berita:", datetime.date.today())
    st.markdown(f"### 🗓️ Jadual Berita Ekonomi — {selected_news_date.strftime('%A, %d %B %Y')}")
    
    # Simulasi data jadual mengikut hari yang dipilih
    day_name = selected_news_date.strftime('%A')
    
    if day_name in ["Saturday", "Sunday"]:
        st.info("☕ Hujung minggu (Weekend) — Pasaran ditutup. Tiada sebarang berita ekonomi atau pergerakan harga aktif.")
    else:
        if day_name == "Wednesday":
            news_data = [
                {"Masa (MYT)": "20:30", "Tahap Impak": "High (Merah)", "Peristiwa": "US CPI / Inflation Rate", "Mata Wang": "USD"},
                {"Masa (MYT)": "22:30", "Tahap Impak": "High (Merah)", "Peristiwa": "Crude Oil Inventories", "Mata Wang": "USD"},
                {"Masa (MYT)": "02:00 (+1 Hari)", "Tahap Impak": "High (Merah)", "Peristiwa": "FOMC Meeting Minutes", "Mata Wang": "USD"}
            ]
        elif day_name == "Thursday":
            news_data = [
                {"Masa (MYT)": "20:30", "Tahap Impak": "High (Merah)", "Peristiwa": "Initial Jobless Claims", "Mata Wang": "USD"},
                {"Masa (MYT)": "20:30", "Tahap Impak": "High (Merah)", "Peristiwa": "Core Retail Sales (MoM)", "Mata Wang": "USD"},
                {"Masa (MYT)": "23:00", "Tahap Impak": "Med (Oren)", "Peristiwa": "Atlanta Fed GDPNow", "Mata Wang": "USD"}
            ]
        elif day_name == "Friday":
            news_data = [
                {"Masa (MYT)": "20:30", "Tahap Impak": "High (Merah)", "Peristiwa": "Non-Farm Payrolls (NFP)", "Mata Wang": "USD"},
                {"Masa (MYT)": "20:30", "Tahap Impak": "High (Merah)", "Peristiwa": "Unemployment Rate", "Mata Wang": "USD"}
            ]
        else:
            news_data = [
                {"Masa (MYT)": "21:00", "Tahap Impak": "Med (Oren)", "Peristiwa": "Prelim GDP / Services PMI", "Mata Wang": "USD"},
                {"Masa (MYT)": "23:00", "Tahap Impak": "Low (Kuning)", "Peristiwa": "CB Consumer Confidence", "Mata Wang": "USD"}
            ]
            
        st.dataframe(pd.DataFrame(news_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### 💡 Panduan Tindakan Trader Semasa Berita High Impact:")
    st.success("""
    * **Elakkan "Open Position" Baru:** Jangan buka posisi sekurang-kurangnya 15 minit sebelum waktu berita berimpak tinggi (*High / Merah*).
    * **Kawalan Risiko:** Pastikan Stop Loss sentiasa dipasang bagi mengelakkan lonjakan harga (*spike*) yang mendadak.
    """)

# 2. DASHBOARD
elif menu == "📊 Dashboard":
    if df_user.empty:
        st.info(f"Belum ada rekod untuk **{trader_name}**. Sila isi data di menu **'Isi Rekod Harian'**.")
    else:
        modal_awal = df_user["Deposit ($)"].iloc[0] if not df_user.empty else 0.0
        balance_akhir = df_user["Balance ($)"].iloc[-1] if not df_user.empty else 0.0
        total_deposit = df_user["Deposit ($)"].sum()
        total_withdrawal = df_user["Withdrawal ($)"].sum()
        total_profit = df_user["Profit ($)"].sum()
        total_loss = df_user["Loss ($)"].sum()
        total_net_pl = df_user["Net P/L ($)"].sum()
        
        win_days_df = df_user[df_user["Profit ($)"] > 0]
        loss_days_df = df_user[df_user["Loss ($)"] > 0]
        
        win_days = len(win_days_df)
        loss_days = len(loss_days_df)
        total_days = len(df_user)
        win_rate = (win_days / total_days) * 100 if total_days > 0 else 0
        
        profit_factor = (total_profit / total_loss) if total_loss > 0 else (total_profit if total_profit > 0 else 0.0)
        
        if total_days > 0:
            avg_win = win_days_df["Profit ($)"].mean() if win_days > 0 else 0.0
            avg_loss = loss_days_df["Loss ($)"].mean() if loss_days > 0 else 0.0
            win_prob = win_days / total_days
            loss_prob = loss_days / total_days
            r_expectancy = (win_prob * avg_win) - (loss_prob * avg_loss)
        else:
            r_expectancy = 0.0
        
        rolling_max = df_user["Balance ($)"].cummax()
        drawdown = df_user["Balance ($)"] - rolling_max
        max_drawdown = drawdown.min() if not drawdown.empty else 0.0

        # Pengiraan Consecutive Wins / Losses
        pl_series = (df_user["Profit ($)"] > 0).astype(int) - (df_user["Loss ($)"] > 0).astype(int)
        max_consec_wins, max_consec_losses, current_streak = 0, 0, 0
        for val in pl_series:
            if val > 0:
                current_streak = current_streak + 1 if current_streak > 0 else 1
                max_consec_wins = max(max_consec_wins, current_streak)
            elif val < 0:
                current_streak = current_streak - 1 if current_streak < 0 else -1
                max_consec_losses = max(max_consec_losses, abs(current_streak))

        # Kotak Metrik Atas (Responsif)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("MODAL AWAL", f"${modal_awal:.2f}")
        m2.metric("BALANCE AKHIR", f"${balance_akhir:.2f}")
        m3.metric("NET P/L ($)", f"${total_net_pl:.2f}", delta=f"${total_net_pl:.2f}")
        m4.metric("WINRATE (%)", f"{win_rate:.1f}%")
        
        st.markdown("---")
        
        col_left, col_right = st.columns([1, 1.4])
        with col_left:
            st.subheader("RINGKASAN & METRIK INSTITUSI")
            summary_table = pd.DataFrame({
                "Perkara": [
                    "Jumlah Deposit ($)", "Jumlah Withdrawal ($)", "Net P/L Keseluruhan",
                    "Jumlah Hari Profit / Loss", "Max Drawdown ($)", "Profit Factor",
                    "R-Expectancy ($)", "Max Consecutive Wins", "Max Consecutive Losses"
                ],
                "Nilai": [
                    f"${total_deposit:.2f}", f"${total_withdrawal:.2f}", f"${total_net_pl:.2f}",
                    f"{win_days}H / {loss_days}H", f"${max_drawdown:.2f}", f"{profit_factor:.2f}",
                    f"${r_expectancy:.2f}", str(max_consec_wins), str(max_consec_losses)
                ]
            })
            st.dataframe(summary_table, use_container_width=True, hide_index=True)
            
        with col_right:
            st.subheader("Grafik Pertumbuhan Balance Gold")
            if "Hari" in df_user.columns and "Balance ($)" in df_user.columns:
                chart_data = df_user.set_index("Hari")[["Balance ($)"]]
                st.line_chart(chart_data, color="#22c55e")

# 3. ISI REKOD HARIAN
elif menu == "📝 Isi Rekod Harian":
    st.subheader(f"Borang Masuk Data Harian & Upload Trade History - [{trader_name}]")
    
    with st.form("daily_form"):
        col1, col2 = st.columns(2)
        with col1:
            hari = st.number_input("Hari Ke-", min_value=1, max_value=31, value=1)
            tarikh = st.date_input("Tarikh", datetime.date.today())
            deposit = st.number_input("Deposit ($)", value=0.00, step=10.0, format="%.2f")
            profit = st.number_input("Profit Harian ($)", value=0.00, step=10.0, format="%.2f")
        with col2:
            loss = st.number_input("Loss Harian ($)", value=0.00, step=10.0, format="%.2f")
            withdrawal = st.number_input("Withdrawal ($)", value=0.00, step=10.0, format="%.2f")
            balance = st.number_input("Balance Terkini ($)", value=0.00, step=10.0, format="%.2f")
            
        uploaded_file = st.file_uploader("Upload Screenshot Trade History (MT4/MT5/Platform)", type=["png", "jpg", "jpeg"])
        notes = st.text_area("Notes / Catatan Ringkasan Harian")
        
        simpan = st.form_submit_button("Simpan Rekod Harian")
        
        if simpan:
            screenshot_path = ""
            if uploaded_file is not None:
                file_name = f"{trader_name}_Day_{hari}_{datetime.date.today()}.png".replace(" ", "_")
                screenshot_path = os.path.join(UPLOAD_DIR, file_name)
                with open(screenshot_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            net_pl = profit - loss
            new_row = pd.DataFrame([{
                "Nama": trader_name,
                "Hari": hari,
                "Tarikh": str(tarikh),
                "Deposit ($)": deposit,
                "Profit ($)": profit,
                "Loss ($)": loss,
                "Net P/L ($)": net_pl,
                "Withdrawal ($)": withdrawal,
                "Balance ($)": balance,
                "Screenshot": screenshot_path,
                "Notes": notes
            }])
            df_all = pd.concat([df_all, new_row], ignore_index=True)
            df_all = df_all.sort_values(by=["Nama", "Hari"]).reset_index(drop=True)
            save_all_data(df_all)
            st.success(f"Rekod harian dan bukti screenshot untuk **{trader_name}** berjaya disimpan!")
            st.balloons()

# 4. PAPARAN JADUAL & EXPORT PDF EKSKLUSIF
elif menu == "📋 Paparan Jadual & Export PDF":
    st.subheader(f"Jadual & Laporan PDF Eksklusif - [{trader_name}]")
    if df_user.empty:
        st.info("Tiada rekod lagi untuk trader ini.")
    else:
        display_df = df_user.drop(columns=["Nama"])
        st.dataframe(display_df, use_column_width=True)
        
        st.markdown("### 🖼️ Semakan Screenshot Trade History")
        has_img = False
        for _, row in df_user.iterrows():
            img_path = str(row.get("Screenshot", ""))
            if img_path and os.path.exists(img_path):
                has_img = True
                with st.expander(f"Hari Ke-{row['Hari']} ({row['Tarikh']}) - Bukti Trade History"):
                    st.image(img_path, caption=f"Trade History Hari {row['Hari']} - {trader_name}", use_column_width=True)
        if not has_img:
            st.info("Tiada fail screenshot yang dimuat naik dalam rekod ini.")
            
        st.markdown("---")
        
        def draw_watermark(canvas, doc):
            canvas.saveState()
            logo_path = "image_15.png"
            if os.path.exists(logo_path):
                canvas.setFillAlpha(0.06)
                canvas.drawImage(logo_path, 80, 250, width=450, height=250, preserveAspectRatio=True, mask='auto')
            canvas.restoreState()

        def generate_exclusive_pdf(dataframe, name):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=30, bottomMargin=30)
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#111827'), spaceAfter=4, alignment=1)
            sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#4b5563'), spaceAfter=15, alignment=1)
            heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#1f2937'), spaceAfter=6)
            
            elements.append(Paragraph(f"<b>PROFLEGACY TRADING INSTITUTION</b>", title_style))
            elements.append(Paragraph(f"Laporan Rasmi Jurnal Gold (XAUUSD) — Trader: <b>{name.upper()}</b> | Tarikh: {datetime.date.today().strftime('%d-%m-%Y')}", sub_style))
            
            t_dep = dataframe["Deposit ($)"].sum()
            t_pro = dataframe["Profit ($)"].sum()
            t_los = dataframe["Loss ($)"].sum()
            t_net = dataframe["Net P/L ($)"].sum()
            
            summary_data = [
                ['Total Deposit', f"${t_dep:.2f}", 'Net P/L Keseluruhan', f"${t_net:.2f}"],
                ['Total Profit', f"${t_pro:.2f}", 'Total Loss', f"${t_los:.2f}"]
            ]
            t_summary = Table(summary_data, colWidths=[130, 130, 130, 130])
            t_summary.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('PADDING', (0,0), (-1,-1), 6),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#1e293b'))
            ]))
            elements.append(t_summary)
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("<b>Log Ringkasan Prestasi Harian</b>", heading_style))
            
            pdf_table_df = dataframe.drop(columns=["Nama", "Screenshot"])
            table_data = [list(pdf_table_df.columns)]
            for _, row in pdf_table_df.iterrows():
                table_data.append([str(val) for val in row.values])
                
            t_data = Table(table_data, repeatRows=1)
            t_data.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 7),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('FONTSIZE', (0,1), (-1,-1), 6),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
            ]))
            elements.append(t_data)
            
            for _, row in dataframe.iterrows():
                img_path = str(row.get("Screenshot", ""))
                if img_path and os.path.exists(img_path):
                    elements.append(Spacer(1, 15))
                    elements.append(Paragraph(f"<b>Bukti Trade History - Hari Ke-{row['Hari']} ({row['Tarikh']})</b>", heading_style))
                    try:
                        elements.append(RLImage(img_path, width=400, height=220, preserveAspectRatio=True))
                    except Exception:
                        pass
            
            doc.build(elements, onFirstPage=draw_watermark, onLaterPages=draw_watermark)
            buffer.seek(0)
            return buffer

        pdf_file = generate_exclusive_pdf(df_user, trader_name)
        st.download_button(
            label="📄 Muat Turun Report PDF Institusi & Bukti Screenshot",
            data=pdf_file,
            file_name=f"ProfLegacy_Exclusive_Report_{trader_name}_{datetime.date.today().strftime('%B_%Y')}.pdf",
            mime="application/pdf"
        )
        
        st.markdown("---")
        if st.button("Padam Rekod Saya"):
            df_all = df_all[df_all["Nama"].str.lower() != trader_name.lower()]
            save_all_data(df_all)
            st.rerun()

# 5. SENARAI PENGGUNA
elif menu == "👥 Senarai Pengguna":
    st.subheader("Senarai Nama Trader Yang Menggunakan Sistem")
    if df_all.empty:
        st.info("Belum ada sebarang data atau trader berdaftar dalam sistem.")
    else:
        active_traders = df_all["Nama"].unique()
        user_summary = []
        for name in active_traders:
            sub_df = df_all[df_all["Nama"] == name]
            total_net = sub_df["Net P/L ($)"].sum()
            total_entries = len(sub_df)
            user_summary.append({
                "Nama Trader": name,
                "Jumlah Hari Rekod": total_entries,
                "Net P/L Terkini ($)": f"${total_net:.2f}"
            })
            
        st.dataframe(pd.DataFrame(user_summary), use_container_width=True, hide_index=True)
        st.success(f"Jumlah keseluruhan trader aktif dalam sistem: {len(active_traders)} orang.")

st.markdown("---")
st.markdown("##### ProfLegacy - Mastering Market Structure & Price Action Precision")
