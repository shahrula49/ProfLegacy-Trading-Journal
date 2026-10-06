import streamlit as st
import pandas as pd
import datetime
import os
from PIL import Image
from io import BytesIO

# --- PENGHASILAN PDF REPORT ---
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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

# --- FUNGSI GENERATE PDF REPORT ---
def generate_pdf_report(dataframe):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=15,
        alignment=1 # Center
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=10
    )
    
    # Tajuk Report
    elements.append(Paragraph("<b>PROFLEGACY - GOLD TRADING JOURNAL REPORT BULANAN</b>", title_style))
    elements.append(Paragraph(f"Tarikh Laporan Dikeluarkan: {datetime.date.today().strftime('%d-%m-%Y')}", heading_style))
    elements.append(Spacer(1, 10))
    
    # Ringkasan Statistik
    total_deposit = dataframe["Deposit ($)"].sum()
    total_profit = dataframe["Profit ($)"].sum()
    total_loss = dataframe["Loss ($)"].sum()
    total_net_pl = dataframe["Net P/L ($)"].sum()
    
    summary_data = [
        ['Total Deposit', f"${total_deposit:.2f}"],
        ['Total Profit', f"${total_profit:.2f}"],
        ['Total Loss', f"${total_loss:.2f}"],
        ['Net P/L Keseluruhan', f"${total_net_pl:.2f}"]
    ]
    
    t_summary = Table(summary_data, colWidths=[200, 200])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f3f4f6')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
    ]))
    
    elements.append(t_summary)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Rekod Harian Trading</b>", heading_style))
    
    # Jadual Data
    if not dataframe.empty:
        table_data = [list(dataframe.columns)]
        for _, row in dataframe.iterrows():
            table_data.append([str(val) for val in row.values])
            
        t_data = Table(table_data, repeatRows=1)
        t_data.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
            ('FONTSIZE', (0,1), (-1,-1), 7),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        elements.append(t_data)
        
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- SIDEBAR ---
try:
    logo_img = Image.open("logo_proflegacy.png")
    st.sidebar.image(logo_img, width=250)
except FileNotFoundError:
    st.sidebar.title("ProfLegacy")

st.sidebar.markdown("---")
menu = st.sidebar.selectbox("Menu", ["📊 Dashboard", "📝 Isi Rekod Harian", "📋 Paparan Jadual & Export PDF"])

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

# 3. PAPARAN JADUAL & EXPORT PDF
elif menu == "📋 Paparan Jadual & Export PDF":
    st.subheader("Jadual Utama & Muat Turun Laporan PDF")
    if df.empty:
        st.info("Tiada rekod lagi untuk dieksport.")
    else:
        st.dataframe(df, use_container_width=True)
        st.markdown("---")
        
        # Butang Download PDF
        pdf_file = generate_pdf_report(df)
        st.download_button(
            label="📄 Muat Turun Report PDF Bulanan",
            data=pdf_file,
            file_name=f"ProfLegacy_Journal_Report_{datetime.date.today().strftime('%B_%Y')}.pdf",
            mime="application/pdf"
        )
        
        st.markdown("---")
        if st.button("Padam Semua Data"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.rerun()

st.markdown("---")
st.markdown("##### ProfLegacy - Mastering Market Structure & Price Action Precision")
