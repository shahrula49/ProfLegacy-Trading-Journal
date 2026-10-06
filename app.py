import streamlit as st
import pandas as pd
import datetime
import os
from PIL import Image
from io import BytesIO
import base64

# --- PENGHASILAN PDF REPORT ---
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(
    page_title="ProfLegacy - Gold Trading Journal",
    layout="wide"
)

# --- CSS KHAS UNTUK BACKGROUND WATERMARK & MOBILE RESPONSIVE ---
def set_background_and_style():
    logo_path = "logo_proflegacy.png"
    encoded_logo = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            encoded_logo = base64.b64encode(f.read()).decode()
            
    css = f"""
    <style>
    /* Tetapan Background Watermark pada Streamlit (Blur/Translucent) */
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.93), rgba(255, 255, 255, 0.93)) {'url(data:image/png;base64,' + encoded_logo + ')' if encoded_logo else ''};
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: fixed;
        background-size: 40% auto;
    }}
    
    /* Mobile-friendly card adjustments */
    @media (max-width: 768px) {{
        .stMetric {{
            background-color: #f8fafc;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_background_and_style()

DATA_FILE = "proflegacy_journal_users.csv"

def load_all_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Nama", "Hari", "Tarikh", "Deposit ($)", "Profit ($)", "Loss ($)", 
            "Net P/L ($)", "Withdrawal ($)", "Balance ($)", "Notes"
        ])

def save_all_data(df):
    df.to_csv(DATA_FILE, index=False)

df_all = load_all_data()

# --- SIDEBAR: PILIH NAMA TRADER & MENU ---
try:
    logo_img = Image.open("logo_proflegacy.png")
    st.sidebar.image(logo_img, width=220)
except FileNotFoundError:
    st.sidebar.title("ProfLegacy")

st.sidebar.markdown("---")
st.sidebar.subheader("Profil Trader")
trader_name = st.sidebar.text_input("Masukkan Nama Anda:", value="Trader 1").strip()

if not trader_name:
    trader_name = "Trader 1"

st.sidebar.markdown("---")
menu = st.sidebar.selectbox("Menu Utama", [
    "📊 Dashboard", 
    "📝 Isi Rekod Harian", 
    "📋 Paparan Jadual & Export PDF",
    "👥 Senarai Pengguna"
])

df_user = df_all[df_all["Nama"].str.lower() == trader_name.lower()] if not df_all.empty else pd.DataFrame(columns=df_all.columns)

st.title(f"📊 GOLD TRADING DASHBOARD | {trader_name.upper()}")
st.markdown("Ringkasan prestasi akaun harian Gold (XAUUSD), deposit, withdrawal, winrate, drawdown, profit factor & R-expectancy.")
st.markdown("---")

# 1. DASHBOARD
if menu == "📊 Dashboard":
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

        # Kotak Metrik Atas (Responsif)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("MODAL AWAL", f"${modal_awal:.2f}")
        m2.metric("BALANCE AKHIR", f"${balance_akhir:.2f}")
        m3.metric("NET P/L ($)", f"${total_net_pl:.2f}", delta=f"${total_net_pl:.2f}")
        m4.metric("WINRATE (%)", f"{win_rate:.1f}%")
        
        st.markdown("---")
        
        col_left, col_right = st.columns([1, 1.4])
        with col_left:
            st.subheader("RINGKASAN & METRIK UTAMA")
            summary_table = pd.DataFrame({
                "Perkara": [
                    "Jumlah Deposit ($)", "Jumlah Withdrawal ($)", "Jumlah Profit ($)",
                    "Jumlah Loss ($)", "Net P/L ($)", "Jumlah Hari Profit",
                    "Jumlah Hari Loss", "Max Drawdown ($)", "Profit Factor", "R-Expectancy ($)"
                ],
                "Nilai": [
                    f"${total_deposit:.2f}", f"${total_withdrawal:.2f}", f"${total_profit:.2f}",
                    f"${total_loss:.2f}", f"${total_net_pl:.2f}", str(win_days),
                    str(loss_days), f"${max_drawdown:.2f}", f"{profit_factor:.2f}", f"${r_expectancy:.2f}"
                ]
            })
            st.dataframe(summary_table, use_container_width=True, hide_index=True)
            
        with col_right:
            st.subheader("Grafik Pertumbuhan Balance Gold")
            if "Hari" in df_user.columns and "Balance ($)" in df_user.columns:
                chart_data = df_user.set_index("Hari")[["Balance ($)"]]
                st.line_chart(chart_data, color="#22c55e")

# 2. ISI REKOD HARIAN
elif menu == "📝 Isi Rekod Harian":
    st.subheader(f"Borang Masuk Data Harian - [{trader_name}]")
    
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
                "Nama": trader_name,
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
            df_all = pd.concat([df_all, new_row], ignore_index=True)
            df_all = df_all.sort_values(by=["Nama", "Hari"]).reset_index(drop=True)
            save_all_data(df_all)
            st.success(f"Rekod harian untuk **{trader_name}** berjaya disimpan!")
            st.balloons()

# 3. PAPARAN JADUAL & EXPORT PDF
elif menu == "📋 Paparan Jadual & Export PDF":
    st.subheader(f"Jadual & Laporan PDF - [{trader_name}]")
    if df_user.empty:
        st.info("Tiada rekod lagi untuk trader ini.")
    else:
        st.dataframe(df_user.drop(columns=["Nama"]), use_container_width=True)
        st.markdown("---")
        
        def draw_watermark(canvas, doc):
            canvas.saveState()
            logo_path = "logo_proflegacy.png"
            if os.path.exists(logo_path):
                # Watermark telus di tengah PDF
                canvas.setFillAlpha(0.08)
                canvas.drawImage(logo_path, 100, 300, width=400, height=200, preserveAspectRatio=True, mask='auto')
            canvas.restoreState()

        def generate_pdf_report(dataframe, name):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#1f2937'), spaceAfter=10, alignment=1)
            heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#374151'), spaceAfter=8)
            
            elements.append(Paragraph(f"<b>PROFLEGACY - GOLD TRADING JOURNAL ({name.upper()})</b>", title_style))
            elements.append(Paragraph(f"Tarikh Laporan: {datetime.date.today().strftime('%d-%m-%Y')}", heading_style))
            elements.append(Spacer(1, 8))
            
            t_dep = dataframe["Deposit ($)"].sum()
            t_pro = dataframe["Profit ($)"].sum()
            t_los = dataframe["Loss ($)"].sum()
            t_net = dataframe["Net P/L ($)"].sum()
            
            summary_data = [
                ['Total Deposit', f"${t_dep:.2f}"],
                ['Total Profit', f"${t_pro:.2f}"],
                ['Total Loss', f"${t_los:.2f}"],
                ['Net P/L Keseluruhan', f"${t_net:.2f}"]
            ]
            t_summary = Table(summary_data, colWidths=[180, 180])
            t_summary.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f3f4f6')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
                ('PADDING', (0,0), (-1,-1), 5),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ]))
            elements.append(t_summary)
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("<b>Rekod Harian Trading</b>", heading_style))
            
            clean_df = dataframe.drop(columns=["Nama"])
            table_data = [list(clean_df.columns)]
            for _, row in clean_df.iterrows():
                table_data.append([str(val) for val in row.values])
                
            t_data = Table(table_data, repeatRows=1)
            t_data.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
                ('FONTSIZE', (0,1), (-1,-1), 7),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')])
            ]))
            elements.append(t_data)
            
            doc.build(elements, onFirstPage=draw_watermark, onLaterPages=draw_watermark)
            buffer.seek(0)
            return buffer

        pdf_file = generate_pdf_report(df_user, trader_name)
        st.download_button(
            label="📄 Muat Turun Report PDF Bulanan",
            data=pdf_file,
            file_name=f"ProfLegacy_Report_{trader_name}_{datetime.date.today().strftime('%B_%Y')}.pdf",
            mime="application/pdf"
        )
        
        st.markdown("---")
        if st.button("Padam Rekod Saya"):
            df_all = df_all[df_all["Nama"].str.lower() != trader_name.lower()]
            save_all_data(df_all)
            st.rerun()

# 4. SENARAI PENGGUNA
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
