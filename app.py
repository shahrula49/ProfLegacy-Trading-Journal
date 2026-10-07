import streamlit as st
import pandas as pd
import datetime
import os
from PIL import Image
from io import BytesIO
import plotly.express as px

# --- PENGHASILAN PDF REPORT (REPORTLAB) ---
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(
    page_title="ProfLegacy - Gold Trading Journal",
    layout="wide"
)

# --- CSS MODEN & JELAS ---
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
    .heatmap-box {
        padding: 8px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        color: white;
        margin: 2px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_clean_style()

DATA_FILE = "proflegacy_journal_users.csv"
PIN_FILE = "proflegacy_user_pins.csv"
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

def load_pins():
    if os.path.exists(PIN_FILE):
        return pd.read_csv(PIN_FILE)
    else:
        return pd.DataFrame(columns=["Nama", "PIN"])

def save_pins(df_pins):
    df_pins.to_csv(PIN_FILE, index=False)

df_all = load_all_data()
df_pins = load_pins()

# --- SIDEBAR: PILIH NAMA TRADER & NAVIGASI ---
try:
    logo_img = Image.open("image_15.png")
    st.sidebar.image(logo_img, width=220)
except FileNotFoundError:
    st.sidebar.title("ProfLegacy")

st.sidebar.markdown("---")
st.sidebar.subheader("Profil & Keselamatan Trader")
trader_name = st.sidebar.text_input("Masukkan Nama Anda:", value="Trader 1").strip()

if not trader_name:
    trader_name = "Trader 1"

# Sistem PIN Profil (Keselamatan Data)
existing_pin_row = df_pins[df_pins["Nama"].str.lower() == trader_name.lower()]
is_pin_protected = not existing_pin_rows_empty = not existing_pin_row.empty

if is_pin_protected:
    entered_pin = st.sidebar.text_input("Masukkan PIN Keselamatan Anda:", type="password", key="login_pin")
    stored_pin = str(existing_pin_row["PIN"].values[0])
    if entered_pin != stored_pin:
        st.sidebar.error("PIN tidak sah! Sila masukkan PIN betul untuk buka akses profil ini.")
        st.stop()
    else:
        st.sidebar.success("Akses Disahkan 🔒")
else:
    set_new_pin = st.sidebar.text_input("Tetapkan PIN Baru (Pilihan):", type="password", key="new_pin")
    if set_new_pin:
        if st.sidebar.button("Daftar PIN Profil"):
            new_pin_df = pd.DataFrame([{"Nama": trader_name, "PIN": set_new_pin}])
            df_pins = pd.concat([df_pins[df_pins["Nama"].str.lower() != trader_name.lower()], new_pin_df], ignore_index=True)
            save_pins(df_pins)
            st.sidebar.success("PIN berjaya didaftarkan!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Menu Navigasi Utama")

menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard", 
    "📝 Isi Rekod Harian", 
    "📋 Paparan Jadual, Heatmap & Export",
    "👥 Senarai Pengguna & Leaderboard"
])

df_user = df_all[df_all["Nama"].str.lower() == trader_name.lower()] if not df_all.empty else pd.DataFrame(columns=df_all.columns)

st.title(f"📊 GOLD TRADING DASHBOARD | {trader_name.upper()}")
st.markdown("Sistem jurnal harian XAUUSD bertaraf institusi dilengkapi analitik lanjutan, kalendar prestasi, dan kawalan keselamatan.")
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

        pl_series = (df_user["Profit ($)"] > 0).astype(int) - (df_user["Loss ($)"] > 0).astype(int)
        max_consec_wins, max_consec_losses, current_streak = 0, 0, 0
        for val in pl_series:
            if val > 0:
                current_streak = current_streak + 1 if current_streak > 0 else 1
                max_consec_wins = max(max_consec_wins, current_streak)
            elif val < 0:
                current_streak = current_streak - 1 if current_streak < 0 else -1
                max_consec_losses = max(max_consec_losses, abs(current_streak))

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
            st.subheader("Grafik Interaktif Pertumbuhan Balance Gold (Plotly)")
            if not df_user.empty and "Tarikh" in df_user.columns:
                fig = px.line(df_user, x="Tarikh", y="Balance ($)", markers=True, title="Trend Pertumbuhan Akaun Mengikut Tarikh")
                fig.update_traces(line_color="#22c55e", marker=dict(size=8))
                fig.update_layout(xaxis_title="Tarikh", yaxis_title="Balance ($)", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

# 2. ISI REKOD HARIAN
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
            st.toast("✅ Rekod harian berjaya disimpan ke dalam sistem!", icon="🚀")
            st.balloons()

# 3. PAPARAN JADUAL, HEATMAP & EXPORT PDF/EXCEL
elif menu == "📋 Paparan Jadual, Heatmap & Export":
    st.subheader(f"Jadual Penapisan Lanjutan, Kalendar Heatmap & Eksport - [{trader_name}]")
    if df_user.empty:
        st.info("Tiada rekod lagi untuk trader ini.")
    else:
        # Penapisan & Carian Lanjutan
        st.markdown("### 🔍 Carian & Penapisan Rekod")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            status_filter = st.selectbox("Tapis Mengikut Prestasi Hari:", ["Semua", "Hari Profit Sahaja", "Hari Loss Sahaja"])
        with f_col2:
            search_query = st.text_input("Cari Kata Kunci dalam Nota:").lower()
            
        filtered_df = df_user.copy()
        if status_filter == "Hari Profit Sahaja":
            filtered_df = filtered_df[filtered_df["Profit ($)"] > 0]
        elif status_filter == "Hari Loss Sahaja":
            filtered_df = filtered_df[filtered_df["Loss ($)"] > 0]
            
        if search_query:
            filtered_df = filtered_df[filtered_df["Notes"].str.lower().str.contains(search_query, na=False)]
            
        st.dataframe(filtered_df.drop(columns=["Nama"]), use_container_width=True)
        
        # Kalendar / Heatmap Bulanan Prestasi
        st.markdown("---")
        st.markdown("### 🗓️ Kalendar Heatmap Prestasi Harian")
        st.markdown("Visual pantas hari untung (Hijau) berbanding hari rugi (Merah):")
        
        cols_heat = st.columns(7)
        days_of_week = ["Isnin", "Selasa", "Rabu", "Khamis", "Jumaat", "Sabtu", "Ahad"]
        for idx, day_name in enumerate(days_of_week):
            cols_heat[idx].markdown(f"**{day_name}**")
            
        # Paparan ringkas grid berdasarkan hari ke- rekod
        grid_cols = st.columns(7)
        for _, row in df_user.iterrows():
            day_num = int(row["Hari"])
            net_val = row["Net P/L ($)"]
            col_idx = (day_num - 1) % 7
            bg_color = "#22c55e" if net_val > 0 else ("#ef4444" if net_val < 0 else "#94a3b8")
            with grid_cols[col_idx]:
                st.markdown(f'<div class="heatmap-box" style="background-color: {bg_color};">H{day_num}<br>${net_val:.1f}</div>', unsafe_allow_html=True)

        st.markdown("---")
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
        st.markdown("### 📥 Muat Turun Laporan")
        
        col_pdf, col_excel = st.columns(2)
        
        with col_pdf:
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
                label="📄 Muat Turun Report PDF Institusi",
                data=pdf_file,
                file_name=f"ProfLegacy_Report_{trader_name}_{datetime.date.today().strftime('%B_%Y')}.pdf",
                mime="application/pdf"
            )
            
        with col_excel:
            output_excel = BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df_user.drop(columns=["Nama"]).to_excel(writer, index=False, sheet_name='Jurnal_Trade')
            output_excel.seek(0)
            
            st.download_button(
                label="📊 Muat Turun Data Excel (.xlsx)",
                data=output_excel,
                file_name=f"ProfLegacy_Journal_{trader_name}_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.markdown("---")
        if st.button("Padam Rekod Saya"):
            df_all = df_all[df_all["Nama"].str.lower() != trader_name.lower()]
            save_all_data(df_all)
            st.toast("⚠️ Rekod akaun anda telah dipadam.", icon="🗑️")
            st.rerun()

# 4. SENARAI PENGGUNA & LEADERBOARD PRESTASI
elif menu == "👥 Senarai Pengguna & Leaderboard":
    st.subheader("👥 Senarai Nama Trader & Leaderboard Prestasi")
    st.markdown(f"*(Nota: Nilai Net P/L ringgit hanya dipaparkan untuk nama pemilik sesi semasa iaitu **{trader_name}**)*")
    
    if df_all.empty:
        st.info("Belum ada sebarang data atau trader berdaftar dalam sistem.")
    else:
        active_traders = df_all["Nama"].unique()
        leaderboard_data = []
        
        for name in active_traders:
            sub_df = df_all[df_all["Nama"] == name]
            total_net = sub_df["Net P/L ($)"].sum()
            total_entries = len(sub_df)
            
            win_d = len(sub_df[sub_df["Profit ($)"] > 0])
            wr = (win_d / total_entries) * 100 if total_entries > 0 else 0.0
            
            t_pro = sub_df["Profit ($)"].sum()
            t_los = sub_df["Loss ($)"].sum()
            pf = (t_pro / t_los) if t_los > 0 else (t_pro if t_pro > 0 else 0.0)
            
            if name.lower() == trader_name.lower():
                net_pl_display = f"${total_net:.2f}"
            else:
                net_pl_display = "🔒 [Rahsia Peribadi]"
                
            leaderboard_data.append({
                "Nama Trader": name,
                "Jumlah Hari": total_entries,
                "Winrate (%)": f"{wr:.1f}%",
                "Profit Factor": f"{pf:.2f}",
                "Net P/L Terkini ($)": net_pl_display
            })
            
        lb_df = pd.DataFrame(leaderboard_data)
        st.dataframe(lb_df, use_container_width=True, hide_index=True)
        st.success(f"Jumlah keseluruhan trader aktif dalam sistem: {len(active_traders)} orang.")

st.markdown("---")
st.markdown("##### ProfLegacy - Mastering Market Structure & Price Action Precision")
