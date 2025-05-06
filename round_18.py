import streamlit as st
import pandas as pd

st.set_page_config(page_title="วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush", layout="wide")
st.title("🛠️ วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

# Input Google Sheets URL
sheet_url = st.text_input("กรอกลิงก์ Google Sheets ที่แชร์แบบสาธารณะ")

if sheet_url:
    try:
        if "/edit" in sheet_url:
            sheet_url = sheet_url.replace("/edit", "/export?format=csv")
        elif "?usp=sharing" in sheet_url:
            sheet_url = sheet_url.replace("?usp=sharing", "/export?format=csv")
        elif not sheet_url.endswith("/export?format=csv"):
            sheet_url += "/export?format=csv"

        df = pd.read_csv(sheet_url)
        st.success("✅ โหลดข้อมูลสำเร็จจาก Google Sheets")
        st.dataframe(df)
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลจาก Google Sheets ได้: {e}")
else:
    st.info("กรุณาใส่ลิงก์ Google Sheets ที่เปิดการเข้าถึงแบบสาธารณะ")
