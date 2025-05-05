
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Brush Wear Rate Dashboard", layout="wide")

st.title("📊 วิเคราะห์อัตราการสึกหรอของ Brush")

# 📂 อัปโหลดไฟล์ Excel
uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ Excel (.xlsx)", type=["xlsx"])
if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)

    # 📌 เลือกจำนวนชีท
    sheet_names = xls.sheet_names
    num_sheets = st.number_input("📌 เลือกจำนวน Sheet ที่ต้องการใช้", min_value=1, max_value=len(sheet_names), value=1)
    selected_sheets = sheet_names[:num_sheets]
    brush_numbers = list(range(1, 33))

    upper_rates, lower_rates = {n:{} for n in brush_numbers}, {n:{} for n in brush_numbers}
    start_upper, start_lower = {}, {}

    for sheet in selected_sheets:
        df_raw = xls.parse(sheet, header=None)
        try:
            hours = float(df_raw.iloc[0, 7])
        except:
            st.warning(f"❌ อ่านชั่วโมงไม่ได้จาก {sheet}")
            continue

        df = xls.parse(sheet, skiprows=1, header=None)

        lower_df = df.iloc[:, 0:3]
        lower_df.columns = ["No_Lower", "Lower_Previous", "Lower_Current"]
        lower_df = lower_df.dropna().apply(pd.to_numeric, errors='coerce')

        upper_df = df.iloc[:, 4:6]
        upper_df.columns = ["Upper_Current", "Upper_Previous"]
        upper_df = upper_df.dropna().apply(pd.to_numeric, errors='coerce')
        upper_df["No_Upper"] = range(1, len(upper_df)+1)

        if sheet == selected_sheets[-1]:
            for n in brush_numbers:
                if not upper_df[upper_df["No_Upper"] == n].empty:
                    start_upper[n] = upper_df[upper_df["No_Upper"] == n].iloc[0]["Upper_Current"]
                if not lower_df[lower_df["No_Lower"] == n].empty:
                    start_lower[n] = lower_df[lower_df["No_Lower"] == n].iloc[0]["Lower_Current"]

        for n in brush_numbers:
            u_row = upper_df[upper_df["No_Upper"] == n]
            if not u_row.empty:
                diff = u_row.iloc[0]["Upper_Current"] - u_row.iloc[0]["Upper_Previous"]
                rate = max(diff / hours, 0)
                upper_rates[n][sheet] = rate

            l_row = lower_df[lower_df["No_Lower"] == n]
            if not l_row.empty:
                diff = l_row.iloc[0]["Lower_Previous"] - l_row.iloc[0]["Lower_Current"]
                rate = max(diff / hours, 0)
                lower_rates[n][sheet] = rate

    # ✅ สร้าง DataFrame
    upper_df = pd.DataFrame.from_dict(upper_rates, orient='index')
    lower_df = pd.DataFrame.from_dict(lower_rates, orient='index')
    brush_number_col = pd.Series(brush_numbers, name="Brush Number")
    upper_df.insert(0, "Brush Number", brush_number_col)
    lower_df.insert(0, "Brush Number", brush_number_col)
    upper_df["Avg Rate (Upper)"] = upper_df.replace(0, np.nan).iloc[:, 1:-1].mean(axis=1)
    lower_df["Avg Rate (Lower)"] = lower_df.replace(0, np.nan).iloc[:, 1:-1].mean(axis=1)

    # ✅ รวมเป็นตาราง
    combined_df = pd.concat([upper_df, lower_df.drop(columns=["Brush Number"])], axis=1)
    combined_df.columns = (
        [f"Upper_{col}" if col not in ["Brush Number", "Avg Rate (Upper)"] else col for col in upper_df.columns] +
        [f"Lower_{col}" if col != "Avg Rate (Lower)" else col for col in lower_df.columns if col != "Brush Number"]
    )

    st.subheader("📋 ตารางเปรียบเทียบอัตราสึกหรอ (Upper / Lower)")
    st.dataframe(combined_df.style.format("{:.6f}"), use_container_width=True)

    # ✅ กราฟ
    x_vals = brush_numbers
    y_upper = upper_df["Avg Rate (Upper)"]
    y_lower = lower_df["Avg Rate (Lower)"]

    st.subheader("📈 กราฟอัตราสึกหรอเฉลี่ยของ Brush")
    fig_combined = go.Figure()
    fig_combined.add_trace(go.Scatter(
        x=x_vals, y=y_upper,
        mode='lines+markers+text',
        name='Upper Avg Rate', line=dict(color='red'),
        text=[str(i) for i in x_vals], textposition='top center'
    ))
    fig_combined.add_trace(go.Scatter(
        x=x_vals, y=y_lower,
        mode='lines+markers+text',
        name='Lower Avg Rate', line=dict(color='darkred'),
        text=[str(i) for i in x_vals], textposition='top center'
    ))
    fig_combined.update_layout(
        title='📈 Average Wear Rate per Brush (1–32)',
        xaxis_title='Brush Number',
        yaxis_title='Wear Rate (mm/hour)',
        template='plotly_white'
    )
    st.plotly_chart(fig_combined, use_container_width=True)
