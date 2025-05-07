
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="เพิ่มข้อมูล Brush", layout="wide")

# โหลด credentials จาก secrets
service_account_info = st.secrets["gcp_service_account"]
spreadsheet_url = st.secrets["spreadsheet_url"]

creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)
worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

st.markdown("### 📝 เพิ่มข้อมูลลง Sheet8 ที่เซลล์ H1 และ Brush Upper/Lower")

# กรอกจำนวนชั่วโมง
input_hour = st.number_input("กรอกจำนวนชั่วโมง", step=0.01)

# ฟอร์มสำหรับ Upper และ Lower
st.markdown("### ⚠️ กรอกค่า Brush (2 ตัวแรกเป็น Upper / 2 ตัวหลังเป็น Lower)")

col1, col2 = st.columns(2)
upper_inputs = []
lower_inputs = []

with col1:
    st.markdown("#### ค่าตัว Upper")
    for i in range(32):
        val = st.number_input(f"ตัวที่ {i+1} (U)", key=f"u{i}")
        upper_inputs.append(val)

with col2:
    st.markdown("#### ค่าตัว Lower")
    for i in range(32):
        val = st.number_input(f"ตัวที่ {i+1} (L)", key=f"l{i}")
        lower_inputs.append(val)

# ปุ่มบันทึก
if st.button("💾 บันทึกข้อมูลลง Google Sheet"):
    try:
        worksheet.update("H1", [[input_hour]])
        for idx, val in enumerate(upper_inputs):
            worksheet.update_cell(idx + 3, 3, val)  # เริ่มจาก C3
        for idx, val in enumerate(lower_inputs):
            worksheet.update_cell(idx + 3, 6, val)  # เริ่มจาก F3
        st.success("✅ บันทึกข้อมูลสำเร็จแล้ว!")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
