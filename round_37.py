
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json

# โหลด service account credentials จาก Streamlit Secrets
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info)
gc = gspread.authorize(creds)

# เปิด Google Sheet และเลือก Sheet8
spreadsheet_url = st.secrets["spreadsheet_url"]
worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

st.markdown("### 📝 เพิ่มข้อมูลลง Sheet8 ที่เซลล์ H1 และ Brush Upper/Lower")

input_hour = st.number_input("กรอกจำนวนชั่วโมง", min_value=0.0, step=1.0, format="%.2f")

st.markdown("### 🔺 กรอกค่า Brush (32 ตัวแรกเป็น Upper / 32 ตัวหลังเป็น Lower)")

upper_values = []
lower_values = []

cols = st.columns(4)
for i in range(32):
    with cols[i % 4]:
        val = st.number_input(f"ตัวที่ {i+1} (U)", key=f"upper_{i}")
        upper_values.append(val)

for i in range(32):
    with cols[i % 4]:
        val = st.number_input(f"ตัวที่ {i+1} (L)", key=f"lower_{i}")
        lower_values.append(val)

if st.button("📥 เพิ่มข้อมูลลง Google Sheet"):
    try:
        # เขียนชั่วโมงที่เซลล์ H1
        worksheet.update("H1", str(input_hour))

        # เขียนค่า Upper ลงใน C3 ถึง C34
        for i in range(32):
            worksheet.update(f"C{i+3}", str(upper_values[i]))

        # เขียนค่า Lower ลงใน F3 ถึง F34
        for i in range(32):
            worksheet.update(f"F{i+3}", str(lower_values[i]))

        st.success("✅ บันทึกข้อมูลสำเร็จแล้ว")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
