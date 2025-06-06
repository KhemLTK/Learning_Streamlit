
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Brush Dashboard", layout="wide")

page = st.sidebar.radio("📂 เลือกหน้า", ["📊 หน้าแสดงผล rate และ ชั่วโมงที่เหลือ", "📝 กรอกข้อมูลแปลงถ่านเพิ่มเติม"])

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

        lower_df_sheet = df.iloc[:, 0:3]
        lower_df_sheet.columns = ["No_Lower", "Lower_Previous", "Lower_Current"]
        lower_df_sheet = lower_df_sheet.dropna().apply(pd.to_numeric, errors='coerce')

        upper_df_sheet = df.iloc[:, 4:6]
        upper_df_sheet.columns = ["Upper_Current", "Upper_Previous"]
        upper_df_sheet = upper_df_sheet.dropna().apply(pd.to_numeric, errors='coerce')
        upper_df_sheet["No_Upper"] = range(1, len(upper_df_sheet) + 1)

        for n in brush_numbers:
            u_row = upper_df_sheet[upper_df_sheet["No_Upper"] == n]
            if not u_row.empty:
                diff = u_row.iloc[0]["Upper_Current"] - u_row.iloc[0]["Upper_Previous"]
                rate = diff / hours if hours > 0 else np.nan
                upper_rates[n][f"Upper_{sheet}"] = rate if rate > 0 else np.nan

            l_row = lower_df_sheet[lower_df_sheet["No_Lower"] == n]
            if not l_row.empty:
                diff = l_row.iloc[0]["Lower_Previous"] - l_row.iloc[0]["Lower_Current"]
                rate = diff / hours if hours > 0 else np.nan
                lower_rates[n][f"Lower_{sheet}"] = rate if rate > 0 else np.nan

    def avg_positive(row):
        valid = row[row > 0]
        return valid.sum() / len(valid) if len(valid) > 0 else np.nan

    upper_df = pd.DataFrame.from_dict(upper_rates, orient='index').fillna(0)
    lower_df = pd.DataFrame.from_dict(lower_rates, orient='index').fillna(0)
    upper_df["Avg Rate (Upper)"] = upper_df.apply(avg_positive, axis=1)
    lower_df["Avg Rate (Lower)"] = lower_df.apply(avg_positive, axis=1)

    avg_rate_upper = upper_df["Avg Rate (Upper)"].tolist()[:32]
    avg_rate_lower = lower_df["Avg Rate (Lower)"].tolist()[:32]

    if "Sheet7" in xls.sheet_names:
        df_sheet7 = xls.parse("Sheet7", header=None)
        upper_current = pd.to_numeric(df_sheet7.iloc[2:34, 5], errors='coerce').values
        lower_current = pd.to_numeric(df_sheet7.iloc[2:34, 2], errors='coerce').values
    else:
        st.error("❌ ไม่พบ Sheet7 สำหรับค่าสภาพปัจจุบัน")
        st.stop()

    def calculate_hours_safe(current, rate):
        return [(c - 35) / r if pd.notna(c) and r and r > 0 and c > 35 else 0 for c, r in zip(current, rate)]

    hour_upper = calculate_hours_safe(upper_current, avg_rate_upper)
    hour_lower = calculate_hours_safe(lower_current, avg_rate_lower)

    st.subheader("📋 ตาราง Avg Rate - Upper")
    def style_upper(val):
        return 'color: red; font-weight: bold' if isinstance(val, float) and val > 0 else ''
    st.dataframe(upper_df.style.applymap(style_upper, subset=["Avg Rate (Upper)"]).format("{:.6f}"), use_container_width=True)

    st.subheader("📋 ตาราง Avg Rate - Lower")
    def style_lower(val):
        return 'color: red; font-weight: bold' if isinstance(val, float) and val > 0 else ''
    st.dataframe(lower_df.style.applymap(style_lower, subset=["Avg Rate (Lower)"]).format("{:.6f}"), use_container_width=True)

    st.subheader("📊 กราฟรวม Avg Rate")
    fig_combined = go.Figure()
    fig_combined.add_trace(go.Scatter(x=brush_numbers, y=avg_rate_upper, mode='lines+markers+text', name='Upper Avg Rate', line=dict(color='red'), text=[str(i) for i in brush_numbers], textposition='top center'))
    fig_combined.add_trace(go.Scatter(x=brush_numbers, y=avg_rate_lower, mode='lines+markers+text', name='Lower Avg Rate', line=dict(color='darkred'), text=[str(i) for i in brush_numbers], textposition='top center'))
    fig_combined.update_layout(xaxis_title='Brush Number', yaxis_title='Wear Rate (mm/hour)', template='plotly_white')
    st.plotly_chart(fig_combined, use_container_width=True)

    st.subheader("🔺 กราฟ Avg Rate - Upper")
    fig_upper = go.Figure()
    fig_upper.add_trace(go.Scatter(x=brush_numbers, y=avg_rate_upper, mode='lines+markers+text', name='Upper Avg Rate', line=dict(color='red'), text=[str(i) for i in brush_numbers], textposition='top center'))
    fig_upper.update_layout(xaxis_title='Brush Number', yaxis_title='Wear Rate (mm/hour)', template='plotly_white')
    st.plotly_chart(fig_upper, use_container_width=True)

    st.subheader("🔻 กราฟ Avg Rate - Lower")
    fig_lower = go.Figure()
    fig_lower.add_trace(go.Scatter(x=brush_numbers, y=avg_rate_lower, mode='lines+markers+text', name='Lower Avg Rate', line=dict(color='darkred'), text=[str(i) for i in brush_numbers], textposition='top center'))
    fig_lower.update_layout(xaxis_title='Brush Number', yaxis_title='Wear Rate (mm/hour)', template='plotly_white')
    st.plotly_chart(fig_lower, use_container_width=True)

    st.subheader("⏳ ชั่วโมงที่เหลือก่อนถึง 35mm (Remaining Life Estimate)")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    color_upper = ['black' if h < 500 else 'red' for h in hour_upper]
    bars1 = ax1.bar(brush_numbers, hour_upper, color=color_upper)
    ax1.set_title("Remaining Hours - Upper")
    ax1.set_ylabel("Hours")
    ax1.set_xticks(brush_numbers)
    for bar, val in zip(bars1, hour_upper):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, f"{int(val)}", ha='center', fontsize=8)

    color_lower = ['black' if h < 500 else 'darkred' for h in hour_lower]
    bars2 = ax2.bar(brush_numbers, hour_lower, color=color_lower)
    ax2.set_title("Remaining Hours - Lower")
    ax2.set_ylabel("Hours")
    ax2.set_xticks(brush_numbers)
    for bar, val in zip(bars2, hour_lower):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, f"{int(val)}", ha='center', fontsize=8)

    plt.tight_layout()
    st.pyplot(fig)

elif page == "📝 กรอกข้อมูลแปลงถ่านเพิ่มเติม":
    st.title("📝 เพิ่มข้อมูลจำนวนชั่วโมง + Brush Upper/Lower 32 ตัว")

    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)

    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/edit?usp=sharing"
    worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

    input_hours = st.number_input("⏱️ กรอกจำนวนชั่วโมง", min_value=0.0, step=0.1)

    st.markdown("### 🔺 กรอกค่า Brush Upper (32 ค่า)")
    upper_values = [st.number_input(f"ตัวที่ {i+1}", key=f"upper_{i}", step=0.01, min_value=0.0) for i in range(32)]

    st.markdown("### 🔻 กรอกค่า Brush Lower (32 ค่า)")
    lower_values = [st.number_input(f"ตัวที่ {i+1}", key=f"lower_{i}", step=0.01, min_value=0.0) for i in range(32)]

    if st.button("📤 บันทึกข้อมูลทั้งหมด"):
        try:
            worksheet.update("H1", [[input_hours]])
            worksheet.update("C3:C34", [[v] for v in upper_values])
            worksheet.update("F3:F34", [[v] for v in lower_values])
            st.success("✅ บันทึกข้อมูลสำเร็จแล้วทั้งหมด")
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")

if page == "📈 พล็อตกราฟความยาวแปรงตามเวลา (แบ่ง Upper / Lower)":
    st.title("📈 พล็อตกราฟความยาวแปรงตามเวลา (แยก Upper และ Lower)")

    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)

    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ"
    sheet = gc.open_by_url(spreadsheet_url)
    sheet_names = [ws.title for ws in sheet.worksheets()]
    selected_sheet = st.selectbox("📄 เลือก Sheet สำหรับ Upper/Lower Current", sheet_names)

    sheet_count = st.number_input("📌 ใช้จำนวน Sheet แรกในการคำนวณ Rate เฉลี่ย", min_value=1, max_value=9, value=6)

    ws = sheet.worksheet(selected_sheet)
    upper_current_values = ws.get("F3:F34")
    lower_current_values = ws.get("C3:C34")

    upper_current = [float(row[0]) if row and row[0] not in ["", "-"] else 0 for row in upper_current_values]
    lower_current = [float(row[0]) if row and row[0] not in ["", "-"] else 0 for row in lower_current_values]

    xls_url = f"https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/export?format=xlsx"
    xls = pd.ExcelFile(xls_url)
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
        df = xls.parse(sheet_name, skiprows=1, header=None)
        df = df.apply(pd.to_numeric, errors='coerce')

        upper_df = df.iloc[:, 4:6]
        upper_df.columns = ["Upper_Current", "Upper_Previous"]
        upper_df["No"] = range(1, len(upper_df)+1)
        for n in brush_numbers:
            row = upper_df[upper_df["No"] == n]
            if not row.empty:
                diff = row.iloc[0]["Upper_Current"] - row.iloc[0]["Upper_Previous"]
                rate = diff / hours if hours > 0 else 0
                upper_rates[n][f"{sheet_name}"] = rate if rate > 0 else 0

        lower_df = df.iloc[:, 0:3]
        lower_df.columns = ["No", "Lower_Previous", "Lower_Current"]
        for n in brush_numbers:
            row = lower_df[lower_df["No"] == n]
            if not row.empty:
                diff = row.iloc[0]["Lower_Previous"] - row.iloc[0]["Lower_Current"]
                rate = diff / hours if hours > 0 else 0
                lower_rates[n][f"{sheet_name}"] = rate if rate > 0 else 0

    def avg_positive(rate_dict):
        valid = [v for v in rate_dict.values() if v > 0]
        return sum(valid) / len(valid) if valid else 0

    avg_rate_upper = [avg_positive(upper_rates[n]) for n in brush_numbers]
    avg_rate_lower = [avg_positive(lower_rates[n]) for n in brush_numbers]

    time_hours = np.arange(0, 201, 10)

    # 🔺 Upper Graph
    fig_upper = go.Figure()
    for i, (start, rate) in enumerate(zip(upper_current, avg_rate_upper)):
        y = [start - (rate * h) for h in time_hours]
        fig_upper.add_trace(go.Scatter(x=time_hours, y=y, mode='lines', name=f"Upper {i+1}"))

    fig_upper.update_layout(
        title="🔺 ความยาวแปรงถ่าน Upper ตามเวลา",
        xaxis_title="ชั่วโมง",
        yaxis_title="ความยาว (mm)",
        xaxis=dict(tickmode='linear', dtick=10, range=[0, 200]),
        yaxis=dict(range=[30, 65]),
        template="plotly_white"
    )
    st.plotly_chart(fig_upper, use_container_width=True)

    # 🔻 Lower Graph
    fig_lower = go.Figure()
    for i, (start, rate) in enumerate(zip(lower_current, avg_rate_lower)):
        y = [start - (rate * h) for h in time_hours]
        fig_lower.add_trace(go.Scatter(x=time_hours, y=y, mode='lines', name=f"Lower {i+1}", line=dict(dash='dot')))

    fig_lower.update_layout(
        title="🔻 ความยาวแปรงถ่าน Lower ตามเวลา",
        xaxis_title="ชั่วโมง",
        yaxis_title="ความยาว (mm)",
        xaxis=dict(tickmode='linear', dtick=10, range=[0, 200]),
        yaxis=dict(range=[30, 65]),
        template="plotly_white"
    )
    st.plotly_chart(fig_lower, use_container_width=True)
