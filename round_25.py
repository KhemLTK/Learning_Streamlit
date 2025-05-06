
import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

# โหลด credentials จาก Streamlit Secret
service_account_info = json.loads(st.secrets["gcp_service_account"])
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)

# ใช้ gspread เชื่อมต่อ Google Sheets
client = gspread.authorize(creds)
sheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/edit"
worksheet = client.open_by_url(sheet_url).worksheet("Sheet8")

# Input จำนวนชั่วโมงที่ต้องการเพิ่ม
st.subheader("📥 เพิ่มข้อมูลแปรงถ่าน")
input_hour = st.number_input("กรอกจำนวนชั่วโมงที่จะเพิ่มไปยัง Sheet8 (คอลัมน์ H1):", min_value=0)

if st.button("➕ เพิ่มข้อมูลแปรงถ่าน"):
    try:
        worksheet.append_row([input_hour])
        st.success(f"เพิ่มข้อมูลสำเร็จ: {input_hour} ชั่วโมงไปยัง Sheet8 แล้ว ✅")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
