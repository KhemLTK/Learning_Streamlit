import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="กรอกข้อมูลแปรงถ่าน", layout="centered")
st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")
st.subheader("📝 เพิ่มข้อมูลจำนวนชั่วโมงลง Sheet8")

# โหลด credentials จาก Secrets
try:
    service_account_info = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"❌ โหลด credentials ไม่สำเร็จ: {e}")
    st.stop()

# เปิด Google Sheet
SHEET_ID = "1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ"
SHEET_NAME = "Sheet8"

try:
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
except Exception as e:
    st.error(f"❌ เปิด Sheet8 ไม่ได้: {e}")
    st.stop()

# ส่วนกรอกข้อมูล
input_hour = st.text_input("กรอกจำนวนชั่วโมงที่จะเพิ่มลงในคอลัมน์ H (เช่น 123.45)")

if st.button("📤 เพิ่มข้อมูลแปรงถ่าน"):
    if input_hour:
        try:
            # เพิ่มข้อมูลไปยังคอลัมน์ H ในแถวถัดไป
            last_row = len(sheet.col_values(8)) + 1  # column H คือ index 8
            sheet.update_cell(last_row, 8, input_hour)
            st.success(f"✅ เพิ่มข้อมูลสำเร็จที่แถว {last_row}: {input_hour}")
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดขณะเพิ่มข้อมูล: {e}")
    else:
        st.warning("⚠️ กรุณากรอกจำนวนชั่วโมงก่อนคลิกปุ่ม")