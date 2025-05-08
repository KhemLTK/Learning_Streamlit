
import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Brush Dashboard", layout="wide")

page = st.sidebar.radio("📂 เลือกหน้า", [
    "📝 กรอกข้อมูลแปลงถ่านเพิ่มเติม",
])

if page == "📝 กรอกข้อมูลแปลงถ่านเพิ่มเติม":
    st.title("📝 กรอกข้อมูลแปรงถ่าน + ชั่วโมง")
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)
    ws = gc.open_by_url("https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ").worksheet("Sheet8")

    hours = st.number_input("⏱️ ชั่วโมง", min_value=0.0, step=0.1)
    st.title("แปลงถ่านส่วน UPPER")
    upper = [st.number_input(f"แปลงถ่านที่ {i+1}", key=f"u{i}", step=0.01) for i in range(32)]
    st.title("แปลงถ่านส่วน Lower")
    lower = [st.number_input(f"แปลงถ่านที่ {i+1}", key=f"l{i}", step=0.01) for i in range(32)]

    if st.button("📤 บันทึก"):
        try:
            ws.update("H1", [[hours]])
            ws.update("C3:C34", [[v] for v in upper])
            ws.update("F3:F34", [[v] for v in lower])
            st.success("✅ บันทึกแล้ว")
        except Exception as e:
            st.error(f"❌ {e}")


    # ------------------ แสดงตารางจากชีตที่เลือก ------------------
    st.subheader("📄 ดูข้อมูลจากชีตที่เลือก")
    xls = pd.ExcelFile("https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/export?format=xlsx")
    sheet_options = [s for s in xls.sheet_names if "Sheet" in s and "Sheet8" not in s]
    selected_view_sheet = st.selectbox("📌 เลือกชีตที่ต้องการดู", sheet_options)

    try:
        df_raw = xls.parse(selected_view_sheet, header=None)
        df = xls.parse(selected_view_sheet, skiprows=1, header=None)

        lower_df_sheet = df.iloc[:, 0:3]
        lower_df_sheet.columns = ["No_Lower", "Lower_Previous", "Lower_Current"]
        lower_df_sheet = lower_df_sheet.dropna().apply(pd.to_numeric, errors='coerce')

        upper_df_sheet = df.iloc[:, 4:6]
        upper_df_sheet.columns = ["Upper_Current", "Upper_Previous"]
        upper_df_sheet = upper_df_sheet.dropna().apply(pd.to_numeric, errors='coerce')
        upper_df_sheet["No_Upper"] = range(1, len(upper_df_sheet) + 1)

        st.markdown("### 🔺 ข้อมูล Upper (Current / Previous)")
        st.dataframe(upper_df_sheet, use_container_width=True)

        st.markdown("### 🔻 ข้อมูล Lower (Previous / Current)")
        st.dataframe(lower_df_sheet, use_container_width=True)
    except Exception as e:
        st.error(f"❌ ไม่สามารถโหลดข้อมูลจากชีตนี้ได้: {e}")

