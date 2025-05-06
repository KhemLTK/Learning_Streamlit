
import streamlit as st
import pandas as pd

st.set_page_config(page_title="วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush", layout="wide")

st.title("🛠️ วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")
st.markdown("## ⏳ ชั่วโมงที่เหลือก่อนถึง 35mm (Remaining Life Estimate)")

# ใช้ลิงก์ Google Sheets ที่ระบุไว้ตายตัว
sheet_id = "1SOkIHJ9jchaJi_0eck5UEyUR8sTn2arndQofmXv5pTdQ"
sheet_name = "Sheet1"
gsheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

try:
    df = pd.read_csv(gsheet_url)
    st.dataframe(df)
except Exception as e:
    st.error(f"ไม่สามารถโหลดข้อมูลจาก Google Sheets ได้: {e}")
