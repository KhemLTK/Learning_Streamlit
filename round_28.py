import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")
st.subheader("📝 เพิ่มข้อมูลจำนวนชั่วโมงลง Sheet8")

# อ่าน Credentials จาก Secrets ที่ตั้งไว้ใน Streamlit Cloud
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)

# ลิงก์ Google Sheet ของคุณ
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1S0kIH9jchaJi_0eck5UEyUR8nTn2arndQxFmxZtw2k8/edit#gid=0"
worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

# รับข้อมูลจากผู้ใช้
input_hours = st.number_input("กรอกจำนวนชั่วโมง", min_value=0.0, step=0.1)

if st.button("➕ เพิ่มข้อมูลจำนวนชั่วโมง"):
    try:
        worksheet.append_row([input_hours])
        st.success(f"เพิ่มข้อมูลสำเร็จ: {input_hours}")
    except Exception as e:
        st.error(f"โหลด credentials ไม่สำเร็จ: {e}")
