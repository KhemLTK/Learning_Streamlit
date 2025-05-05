
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush", layout="wide")
st.title("🛠️ วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel (.xlsx)", type=["xlsx"])
if uploaded_file:
    df_all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(df_all_sheets.keys())
    selected_sheet = st.selectbox("📌 เลือกจำนวน Sheet ที่ต้องการใช้ (สำหรับคำนวณ Avg Rate)", sheet_names)

    df = df_all_sheets[selected_sheet]
    df.fillna(0, inplace=True)

    upper_columns = [col for col in df.columns if "Upper_Sheet" in col]
    lower_columns = [col for col in df.columns if "Lower_Sheet" in col]

    df["Avg Rate (Upper)"] = df[upper_columns].replace('None', 0).astype(float).mean(axis=1)
    df["Avg Rate (Lower)"] = df[lower_columns].replace('None', 0).astype(float).mean(axis=1)

    def calculate_hours_safe(current, rate):
        hours = []
        for c, r in zip(current, rate):
            try:
                h = max(0, (35 - float(c)) / float(r)) if r != 0 else 0
            except:
                h = 0
            hours.append(round(h))
        return hours

    upper_current = [20] * len(df)
    lower_current = [20] * len(df)
    avg_rate_upper = df["Avg Rate (Upper)"]
    avg_rate_lower = df["Avg Rate (Lower)"]

    hour_upper = calculate_hours_safe(upper_current, avg_rate_upper)
    hour_lower = calculate_hours_safe(lower_current, avg_rate_lower)

    brush_numbers = list(range(1, len(df) + 1))

    st.subheader("⏳ ชั่วโมงที่เหลือก่อนถึง 35mm (Remaining Life Estimate)")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

    color_upper = ['black' if h < 500 else 'red' for h in hour_upper]
    bars1 = ax1.bar(brush_numbers, hour_upper, color=color_upper)
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 10, yval, ha='center', va='bottom')

    ax1.set_title('Remaining Hours - Upper')
    ax1.set_ylabel('Hours')

    color_lower = ['black' if h < 500 else 'darkred' for h in hour_lower]
    bars2 = ax2.bar(brush_numbers, hour_lower, color=color_lower)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 10, yval, ha='center', va='bottom')

    ax2.set_title('Remaining Hours - Lower')
    ax2.set_ylabel('Hours')

    st.pyplot(fig)
