
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

def avg_positive(rate_dict):
    valid = [v for v in rate_dict.values() if v > 0]
    return sum(valid) / len(valid) if valid else 0

st.set_page_config(page_title="พล็อตกราฟแปรงถ่าน", layout="wide")

page = st.sidebar.radio("📂 เลือกหน้า", ["📈 พล็อตกราฟตามเวลา (แยก Upper และ Lower)"])

if page == "📈 พล็อตกราฟตามเวลา (แยก Upper และ Lower)":
    st.title("📈 พล็อตกราฟตามเวลา (แยก Upper และ Lower)")

    # 🔐 Load credentials
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)

    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ"
    sheet = gc.open_by_url(spreadsheet_url)

    sheet_names = [ws.title for ws in sheet.worksheets()]
    selected_sheet = st.selectbox("📄 เลือก Sheet ที่ใช้ค่าปัจจุบัน", sheet_names)

    sheet_count = st.number_input("📌 จำนวน Sheet ที่ใช้ในการคำนวณ Rate เฉลี่ย", min_value=1, max_value=9, value=6)

    # ✅ Read current values
    ws = sheet.worksheet(selected_sheet)
    upper_current = [float(row[0]) if row and row[0] not in ["", "-"] else 0 for row in ws.get("F3:F34")]
    lower_current = [float(row[0]) if row and row[0] not in ["", "-"] else 0 for row in ws.get("C3:C34")]

    # ✅ Load rate from first N sheets
    xls = pd.ExcelFile("https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/export?format=xlsx")
    selected_sheets = xls.sheet_names[:sheet_count]
    brush_numbers = list(range(1, 33))

    upper_rates = {n:{} for n in brush_numbers}
    lower_rates = {n:{} for n in brush_numbers}

    for sheet_name in selected_sheets:
        df_raw = xls.parse(sheet_name, header=None)
        try:
            hours = float(df_raw.iloc[0, 7])
        except:
            continue
        df = xls.parse(sheet_name, skiprows=1, header=None).apply(pd.to_numeric, errors='coerce')

        upper_df = df.iloc[:, 4:6]
        upper_df.columns = ["Upper_Current", "Upper_Previous"]
        upper_df["No"] = range(1, len(upper_df)+1)

        lower_df = df.iloc[:, 0:3]
        lower_df.columns = ["No", "Lower_Previous", "Lower_Current"]

        for n in brush_numbers:
            u_row = upper_df[upper_df["No"] == n]
            if not u_row.empty:
                diff = u_row.iloc[0]["Upper_Current"] - u_row.iloc[0]["Upper_Previous"]
                rate = diff / hours if hours > 0 else 0
                if rate > 0:
                    upper_rates[n][sheet_name] = rate

            l_row = lower_df[lower_df["No"] == n]
            if not l_row.empty:
                diff = l_row.iloc[0]["Lower_Previous"] - l_row.iloc[0]["Lower_Current"]
                rate = diff / hours if hours > 0 else 0
                if rate > 0:
                    lower_rates[n][sheet_name] = rate

    avg_rate_upper = [avg_positive(upper_rates[n]) for n in brush_numbers]
    avg_rate_lower = [avg_positive(lower_rates[n]) for n in brush_numbers]

    time_hours = np.arange(0, 201, 10)

    # 🔺 Upper Plot
    fig_upper = go.Figure()
    for i, (start, rate) in enumerate(zip(upper_current, avg_rate_upper)):
        y = [start - rate*t for t in time_hours]
        fig_upper.add_trace(go.Scatter(x=time_hours, y=y, mode="lines", name=f"Upper {i+1}"))
    fig_upper.update_layout(
        title="🔺 ความยาวแปรงถ่าน Upper ตามเวลา",
        xaxis_title="ชั่วโมง", yaxis_title="ความยาว (mm)",
        xaxis=dict(dtick=10, range=[0, 200]), yaxis=dict(range=[30, 65]),
        template="plotly_white"
    )
    st.plotly_chart(fig_upper, use_container_width=True)

    # 🔻 Lower Plot
    fig_lower = go.Figure()
    for i, (start, rate) in enumerate(zip(lower_current, avg_rate_lower)):
        y = [start - rate*t for t in time_hours]
        fig_lower.add_trace(go.Scatter(x=time_hours, y=y, mode="lines", name=f"Lower {i+1}", line=dict(dash="dot")))
    fig_lower.update_layout(
        title="🔻 ความยาวแปรงถ่าน Lower ตามเวลา",
        xaxis_title="ชั่วโมง", yaxis_title="ความยาว (mm)",
        xaxis=dict(dtick=10, range=[0, 200]), yaxis=dict(range=[30, 65]),
        template="plotly_white"
    )
    st.plotly_chart(fig_lower, use_container_width=True)
