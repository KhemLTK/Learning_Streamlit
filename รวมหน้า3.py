
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Brush Dashboard", layout="wide")

# Navigation
page = st.sidebar.radio("📂 เลือกหน้า", ["📈 พล็อตกราฟความยาวแปรงตามเวลา"])

if page == "📈 พล็อตกราฟความยาวแปรงตามเวลา":
    st.title("📈 พล็อตกราฟความยาวแปรงตามเวลา (Upper)")

    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)

    # ให้ผู้ใช้เลือก Sheet ที่จะใช้ (เช่น Sheet1 ถึง Sheet9)
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ"
    sheet = gc.open_by_url(spreadsheet_url)

    sheet_names = [ws.title for ws in sheet.worksheets()]
    selected_sheet = st.selectbox("📄 เลือก Sheet ที่ใช้ค่าปัจจุบัน (Upper Current)", sheet_names)

    # อ่าน Upper current จาก sheet ที่เลือก (คอลัมน์ F, แถว 3 ถึง 34)
    ws = sheet.worksheet(selected_sheet)
    upper_current_values = ws.get("F3:F34")
    upper_current = [float(row[0]) if row and row[0] not in ["", "-"] else 0 for row in upper_current_values]

    # อ่าน avg rate จาก 7 sheet แรก (แบบที่เคยทำ)
    avg_rate_sheet_url = f"https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/export?format=xlsx"
    xls = pd.ExcelFile(avg_rate_sheet_url)
    brush_numbers = list(range(1, 33))
    selected_sheets = xls.sheet_names[:7]  # คำนวณเฉพาะ 7 แผ่นแรก

    upper_rates = {n:{} for n in brush_numbers}
    for sheet_name in selected_sheets:
        df_raw = xls.parse(sheet_name, header=None)
        try:
            hours = float(df_raw.iloc[0, 7])
        except:
            continue
        df = xls.parse(sheet_name, skiprows=1, header=None)
        upper_df_sheet = df.iloc[:, 4:6]
        upper_df_sheet.columns = ["Upper_Current", "Upper_Previous"]
        upper_df_sheet = upper_df_sheet.dropna().apply(pd.to_numeric, errors='coerce')
        upper_df_sheet["No_Upper"] = range(1, len(upper_df_sheet)+1)
        for n in brush_numbers:
            row = upper_df_sheet[upper_df_sheet["No_Upper"] == n]
            if not row.empty:
                diff = row.iloc[0]["Upper_Current"] - row.iloc[0]["Upper_Previous"]
                rate = diff / hours if hours > 0 else 0
                upper_rates[n][f"Upper_{sheet_name}"] = rate if rate > 0 else 0

    def avg_positive(row):
        valid = [v for v in row.values() if v > 0]
        return sum(valid) / len(valid) if valid else 0

    avg_rate_upper = [avg_positive(upper_rates[n]) for n in brush_numbers]

    # สร้างแกนเวลา 0-100 ชั่วโมง
    time_hours = np.arange(0, 101, 10)
    fig = go.Figure()

    for i, (initial, rate) in enumerate(zip(upper_current, avg_rate_upper)):
        y_values = [initial - (rate * t) for t in time_hours]
        fig.add_trace(go.Scatter(x=time_hours, y=y_values, mode='lines+markers', name=f"Brush {i+1}"))

    fig.update_layout(
        title="ความยาวแปรงถ่านตามเวลา (Upper, คำนวณจากค่าเริ่มต้น - rate * ชั่วโมง)",
        xaxis_title="ชั่วโมง",
        yaxis_title="ความยาว (mm)",
        xaxis=dict(tickmode='linear', dtick=10, range=[0, 100]),
        yaxis=dict(range=[30, 65]),
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)
