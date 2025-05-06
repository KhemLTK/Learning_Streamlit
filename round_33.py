
import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

# โหลด credentials จาก secrets
service_account_info = json.loads(st.secrets["gcp_service_account"])
creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)

# URL ของ Google Sheet และชื่อชีต
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/edit#gid=1747819137"
worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

st.markdown("### 📝 เพิ่มข้อมูลลง Sheet8 ที่เซลล์ H1 และ Brush Upper/Lower")

# ช่องกรอกจำนวนชั่วโมง
hours = st.number_input("⏱️ กรอกจำนวนชั่วโมง", min_value=0.0, step=1.0)

# สร้าง input สำหรับ 32 ตัว (แบ่งเป็น 16+16)
st.markdown("### ⚠️ กรอกค่า Brush (ตัวที่ 1–16 = Upper / 17–32 = Lower)")
cols = st.columns(2)
upper_values = []
lower_values = []

for i in range(16):
    with cols[0]:
        val = st.number_input(f"ตัวที่ {i+1}", key=f"u{i+1}", step=0.1)
        upper_values.append(val)

for i in range(16):
    with cols[1]:
        val = st.number_input(f"ตัวที่ {i+17}", key=f"l{i+17}", step=0.1)
        lower_values.append(val)

# ปุ่มบันทึก
if st.button("📥 เพิ่มข้อมูลลง Google Sheet"):
    try:
        worksheet.update("H1", str(hours))  # ชั่วโมงไปลงช่อง H1
        worksheet.batch_update([
            {"range": "C3:C18", "values": [[v] for v in upper_values]},
            {"range": "F3:F18", "values": [[v] for v in lower_values]}
        ])
        st.success("✅ เพิ่มข้อมูลสำเร็จเรียบร้อยแล้ว")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
