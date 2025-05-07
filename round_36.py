
import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials

# โหลด service account จาก secrets โดยไม่ต้อง json.loads()
service_account_info = st.secrets["gcp_service_account"]
CREDS = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(CREDS)

# ลิงก์ Google Sheets และชื่อชีต
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/edit#gid=0"
worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

# UI
st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

st.subheader("📝 เพิ่มข้อมูลลง Sheet8 ที่เซลล์ H1 และ Brush Upper/Lower")
hours = st.number_input("กรอกจำนวนชั่วโมง", min_value=0.0, step=1.0, key="hour_input")

# ช่องสำหรับ Upper และ Lower อย่างละ 32 ตัว
st.markdown("🔺 กรอกค่า Brush (2 ตัวแรกเป็น Upper / 2 ตัวหลังเป็น Lower)")

cols = st.columns(4)
upper_values = []
lower_values = []

for i in range(32):
    with cols[i % 4]:
        u = st.number_input(f"ตัวที่ {i+1} (U)", key=f"upper_{i}")
        upper_values.append(u)

st.divider()

for i in range(32):
    with cols[i % 4]:
        l = st.number_input(f"ตัวที่ {i+1} (L)", key=f"lower_{i}")
        lower_values.append(l)

# ปุ่มเพิ่มข้อมูล
if st.button("➕ เพิ่มข้อมูลลง Google Sheet"):
    try:
        worksheet.update("H1", [[hours]])
        worksheet.update("C3:C34", [[v] for v in upper_values])
        worksheet.update("F3:F34", [[v] for v in lower_values])
        st.success("✅ เพิ่มข้อมูลสำเร็จ")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
