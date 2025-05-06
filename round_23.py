
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# อ่านข้อมูลจาก Secrets (service_account JSON)
service_account_info = st.secrets["GOOGLE_SERVICE_ACCOUNT"]
creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)

# เชื่อมต่อ Google Sheet
SHEET_ID = "1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ"
SHEET_NAME = "Sheet8"
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ส่วน UI
st.title("🔧 เพิ่มข้อมูลแปรงถ่านลงใน Google Sheet")
st.markdown("📌 ใส่จำนวนชั่วโมง แล้วเพิ่มลงไปที่ช่อง `H1` ใน Sheet8")

input_hour = st.number_input("📥 กรอกจำนวนชั่วโมง", min_value=0.0, format="%.2f")

if st.button("✅ เพิ่มข้อมูลแปรงถ่าน"):
    try:
        worksheet.update("H1", [[input_hour]])
        st.success(f"✅ เพิ่มข้อมูล {input_hour} ไปยังช่อง H1 เรียบร้อยแล้ว")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
