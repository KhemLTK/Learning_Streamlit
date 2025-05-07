
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Brush Dashboard", layout="wide")

# --- Sidebar navigation ---
page = st.sidebar.radio("📂 เลือกหน้า", ["📊 หน้าแสดงผล rate และ ชั่วโมงที่เหลือ", "📝 กรอกข้อมูลแปลงถ่านเพิ่มเติม", "📈 พล็อตกราฟตามเวลา (Upper / Lower)"])

# ------------------ PAGE 1 ------------------
if page == "📊 หน้าแสดงผล rate และ ชั่วโมงที่เหลือ":
    st.title("🛠️ วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")
    sheet_id = "1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    xls = pd.ExcelFile(sheet_url)
    sheet_names = xls.sheet_names

    num_sheets = st.number_input("📌 เลือกจำนวน Sheet ที่ต้องการใช้ (สำหรับคำนวณ Avg Rate)", min_value=1, max_value=len(sheet_names), value=7)
    selected_sheets = sheet_names[:num_sheets]
    brush_numbers = list(range(1, 33))

    upper_rates, lower_rates = {n:{} for n in brush_numbers}, {n:{} for n in brush_numbers}

    for sheet in selected_sheets:
        df_raw = xls.parse(sheet, header=None)
        try:
            hours = float(df_raw.iloc[0, 7])
        except:
            continue
        df = xls.parse(sheet, skiprows=1, header=None)
        df = df.apply(pd.to_numeric, errors='coerce')

        lower_df = df.iloc[:, 0:3]
        lower_df.columns = ["No_Lower", "Lower_Previous", "Lower_Current"]

        upper_df = df.iloc[:, 4:6]
        upper_df.columns = ["Upper_Current", "Upper_Previous"]
        upper_df["No_Upper"] = range(1, len(upper_df)+1)

        for n in brush_numbers:
            u = upper_df[upper_df["No_Upper"] == n]
            if not u.empty:
                diff = u.iloc[0]["Upper_Current"] - u.iloc[0]["Upper_Previous"]
                rate = diff / hours if hours > 0 else np.nan
                upper_rates[n][sheet] = rate if rate > 0 else np.nan

            l = lower_df[lower_df["No_Lower"] == n]
            if not l.empty:
                diff = l.iloc[0]["Lower_Previous"] - l.iloc[0]["Lower_Current"]
                rate = diff / hours if hours > 0 else np.nan
                lower_rates[n][sheet] = rate if rate > 0 else np.nan

    def avg_positive(row):
        valid = [v for v in row.values() if v > 0]
        return sum(valid) / len(valid) if valid else 0

    upper_df = pd.DataFrame({n: upper_rates[n] for n in brush_numbers}).T
    lower_df = pd.DataFrame({n: lower_rates[n] for n in brush_numbers}).T
    upper_df["Avg Rate (Upper)"] = upper_df.apply(avg_positive, axis=1)
    lower_df["Avg Rate (Lower)"] = lower_df.apply(avg_positive, axis=1)
    avg_rate_upper = upper_df["Avg Rate (Upper)"].tolist()
    avg_rate_lower = lower_df["Avg Rate (Lower)"].tolist()

    if "Sheet7" in xls.sheet_names:
        df_sheet7 = xls.parse("Sheet7", header=None)
        upper_current = pd.to_numeric(df_sheet7.iloc[2:34, 5], errors='coerce').values
        lower_current = pd.to_numeric(df_sheet7.iloc[2:34, 2], errors='coerce').values
    else:
        st.error("❌ ไม่พบ Sheet7 สำหรับค่าสภาพปัจจุบัน")
        st.stop()

    def calculate_hours_safe(current, rate):
        return [(c - 35) / r if pd.notna(c) and r > 0 and c > 35 else 0 for c, r in zip(current, rate)]

    hour_upper = calculate_hours_safe(upper_current, avg_rate_upper)
    hour_lower = calculate_hours_safe(lower_current, avg_rate_lower)

    st.subheader("📋 ตาราง Avg Rate - Upper")
    st.dataframe(upper_df.style.format("{:.6f}"), use_container_width=True)
    st.subheader("📋 ตาราง Avg Rate - Lower")
    st.dataframe(lower_df.style.format("{:.6f}"), use_container_width=True)

    st.subheader("📊 กราฟรวม Avg Rate")
    fig_combined = go.Figure()
    fig_combined.add_trace(go.Scatter(x=brush_numbers, y=avg_rate_upper, name='Upper Avg Rate', line=dict(color='red')))
    fig_combined.add_trace(go.Scatter(x=brush_numbers, y=avg_rate_lower, name='Lower Avg Rate', line=dict(color='darkred')))
    fig_combined.update_layout(xaxis_title='Brush Number', yaxis_title='Wear Rate (mm/hour)', template='plotly_white')
    st.plotly_chart(fig_combined, use_container_width=True)

    st.subheader("⏳ ชั่วโมงที่เหลือก่อนถึง 35mm")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    ax1.bar(brush_numbers, hour_upper, color='red')
    ax1.set_title("Remaining Hours - Upper")
    ax2.bar(brush_numbers, hour_lower, color='darkred')
    ax2.set_title("Remaining Hours - Lower")
    plt.tight_layout()
    st.pyplot(fig)

# ------------------ PAGE 2 ------------------
elif page == "📝 กรอกข้อมูลแปลงถ่านเพิ่มเติม":
    st.title("📝 เพิ่มข้อมูลจำนวนชั่วโมง + Brush Upper/Lower 32 ตัว")
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)
    worksheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ").worksheet("Sheet8")

    input_hours = st.number_input("⏱️ กรอกจำนวนชั่วโมง", min_value=0.0, step=0.1)
    st.markdown("### 🔺 กรอกค่า Brush Upper (32 ค่า)")
    upper_values = [st.number_input(f"Upper {i+1}", step=0.01, key=f"u{i}") for i in range(32)]
    st.markdown("### 🔻 กรอกค่า Brush Lower (32 ค่า)")
    lower_values = [st.number_input(f"Lower {i+1}", step=0.01, key=f"l{i}") for i in range(32)]

    if st.button("📤 บันทึกข้อมูลทั้งหมด"):
        try:
            worksheet.update("H1", [[input_hours]])
            worksheet.update("C3:C34", [[v] for v in upper_values])
            worksheet.update("F3:F34", [[v] for v in lower_values])
            st.success("✅ บันทึกข้อมูลสำเร็จแล้ว")
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# ------------------ PAGE 3 ------------------
elif page == "📈 พล็อตกราฟตามเวลา (Upper / Lower)":
    st.title("📈 พล็อตกราฟตามเวลา (แยก Upper และ Lower)")

    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)
    sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ")

    sheet_names = [ws.title for ws in sheet.worksheets()]
    selected_sheet = st.selectbox("📄 เลือก Sheet สำหรับ Current", sheet_names)
    sheet_count = st.number_input("📌 ใช้จำนวน Sheet แรกในการคำนวณ Rate", min_value=1, max_value=9, value=6)

    ws = sheet.worksheet(selected_sheet)
    upper_current = [float(row[0]) if row and row[0] not in ["", "-"] else 0 for row in ws.get("F3:F34")]
    lower_current = [float(row[0]) if row and row[0] not in ["", "-"] else 0 for row in ws.get("C3:C34")]

    xls = pd.ExcelFile("https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/export?format=xlsx")
    selected_sheets = xls.sheet_names[:sheet_count]
    brush_numbers = list(range(1, 33))

    def calc_avg_rate(pos, col_diff):
        rates = {n: [] for n in brush_numbers}
        for s in selected_sheets:
            df = xls.parse(s, skiprows=1, header=None).apply(pd.to_numeric, errors='coerce')
            try: hours = float(xls.parse(s, header=None).iloc[0, 7])
            except: continue
            for i in brush_numbers:
                curr = df.iloc[i-1, pos]
                prev = df.iloc[i-1, pos+1]
                if pd.notna(curr) and pd.notna(prev) and hours > 0:
                    rate = (curr - prev) / hours if col_diff == 'up' else (prev - curr) / hours
                    if rate > 0: rates[i].append(rate)
        return [np.mean(rates[n]) if rates[n] else 0 for n in brush_numbers]

    avg_rate_upper = calc_avg_rate(4, 'up')
    avg_rate_lower = calc_avg_rate(1, 'low')
    time_hours = np.arange(0, 201, 10)

    fig_upper = go.Figure()
    for i, (start, rate) in enumerate(zip(upper_current, avg_rate_upper)):
        y = [start - rate*t for t in time_hours]
        fig_upper.add_trace(go.Scatter(x=time_hours, y=y, name=f"Upper {i+1}", mode='lines'))

    fig_upper.update_layout(title="🔺 ความยาว Upper ตามเวลา", xaxis_title="ชั่วโมง", yaxis_title="ความยาว (mm)",
                            xaxis=dict(dtick=10, range=[0, 200]), yaxis=dict(range=[30, 65]))

    st.plotly_chart(fig_upper, use_container_width=True)

    fig_lower = go.Figure()
    for i, (start, rate) in enumerate(zip(lower_current, avg_rate_lower)):
        y = [start - rate*t for t in time_hours]
        fig_lower.add_trace(go.Scatter(x=time_hours, y=y, name=f"Lower {i+1}", mode='lines', line=dict(dash='dot')))

    fig_lower.update_layout(title="🔻 ความยาว Lower ตามเวลา", xaxis_title="ชั่วโมง", yaxis_title="ความยาว (mm)",
                            xaxis=dict(dtick=10, range=[0, 200]), yaxis=dict(range=[30, 65]))

    st.plotly_chart(fig_lower, use_container_width=True)
