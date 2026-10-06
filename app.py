import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Gold Trading Journal", page_icon="📈", layout="wide"
)

st.title("🥇 Gold Trading Journal & Dashboard (Oktober)")

# Load data dari Excel
excel_path = "Trading Journal.xlsx"

try:
  df_dashboard = pd.read_excel(excel_path, sheet_name="Dashboard")
  df_journal = pd.read_excel(excel_path, sheet_name="Trading Journal", skiprows=1)

  # Papar Dashboard
  st.subheader("📊 Ringkasan Dashboard")
  st.dataframe(df_dashboard, use_container_width=True)

  # Papar Journal
  st.subheader("📅 Rekod Trading Journal Harian")
  st.dataframe(df_journal, use_container_width=True)

except Exception as e:
  st.error(
      f"Ralat membaca fail Excel: {e}. Sila pastikan fail 'Trading Journal.xlsx'"
      " telah diupload."
  )