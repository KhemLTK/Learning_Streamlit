import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# ต้องเป็นคำสั่งแรก
st.set_page_config(page_title="Brush Wear Rate Dashboard", layout="wide")

st.title("🛠️ วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names[:7]
    brush_numbers = list(range(1, 33))
    upper_rates, lower_rates = {n: {} for n in brush_numbers}, {n: {} for n in brush_numbers}

    for sheet in sheet_names:
        df_raw = xls.parse(sheet, header=None)
        try:
            hours = float(df_raw.iloc[0, 7])
        except:
            continue
        df = xls.parse(sheet, skiprows=1, header=None)

        lower_df = df.iloc[:, 0:3]
        lower_df.columns = ["No_Lower", "Lower_Previous", "Lower_Current"]
        lower_df = lower_df.dropna().apply(pd.to_numeric, errors='coerce')

        upper_df = df.iloc[:, 4:6]
        upper_df.columns = ["Upper_Current", "Upper_Previous"]
        upper_df = upper_df.dropna().apply(pd.to_numeric, errors='coerce')
        upper_df["No_Upper"] = range(1, len(upper_df) + 1)

        for n in brush_numbers:
            u_row = upper_df[upper_df["No_Upper"] == n]
            if not u_row.empty:
                diff = u_row.iloc[0]["Upper_Current"] - u_row.iloc[0]["Upper_Previous"]
                rate = diff / hours if hours > 0 else np.nan
                upper_rates[n][sheet] = rate

            l_row = lower_df[lower_df["No_Lower"] == n]
            if not l_row.empty:
                diff = l_row.iloc[0]["Lower_Previous"] - l_row.iloc[0]["Lower_Current"]
                rate = diff / hours if hours > 0 else np.nan
                lower_rates[n][sheet] = rate

    def avg_positive(row):
        valid = row[row > 0]
        return valid.sum() / len(valid) if len(valid) > 0 else np.nan

    upper_df = pd.DataFrame.from_dict(upper_rates, orient='index')
    lower_df = pd.DataFrame.from_dict(lower_rates, orient='index')
    upper_df["Avg Rate (Upper)"] = upper_df.apply(avg_positive, axis=1)
    lower_df["Avg Rate (Lower)"] = lower_df.apply(avg_positive, axis=1)

    avg_rate_upper = upper_df["Avg Rate (Upper)"].tolist()[:32]
    avg_rate_lower = lower_df["Avg Rate (Lower)"].tolist()[:32]

    df_sheet7 = xls.parse("Sheet7", header=None)
    upper_current = pd.to_numeric(df_sheet7.iloc[2:34, 5], errors='coerce').values
    lower_current = pd.to_numeric(df_sheet7.iloc[2:34, 2], errors='coerce').values

    def calculate_hours_safe(current, rate):
        return [(c - 35) / r if pd.notna(c) and r and r > 0 and c > 35 else 0 for c, r in zip(current, rate)]

    hour_upper = calculate_hours_safe(upper_current, avg_rate_upper)
    hour_lower = calculate_hours_safe(lower_current, avg_rate_lower)

    color_upper = ['black' if val < 500 else 'red' for val in hour_upper]
    color_lower = ['black' if val < 500 else 'darkred' for val in hour_lower]

    st.subheader("⏳ ชั่วโมงที่เหลือก่อนถึง 35mm (Remaining Life Estimate)")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

    bars1 = ax1.bar(brush_numbers, hour_upper, color=color_upper)
    ax1.set_title("Remaining Hours - Upper")
    ax1.set_ylabel("Hours")
    ax1.set_xticks(brush_numbers)
    for bar, val in zip(bars1, hour_upper):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, f"{int(val)}", ha='center', fontsize=8)

    bars2 = ax2.bar(brush_numbers, hour_lower, color=color_lower)
    ax2.set_title("Remaining Hours - Lower")
    ax2.set_ylabel("Hours")
    ax2.set_xticks(brush_numbers)
    for bar, val in zip(bars2, hour_lower):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, f"{int(val)}", ha='center', fontsize=8)

    plt.tight_layout()
    st.pyplot(fig)
