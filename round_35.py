
import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials

# โหลด credentials จาก Streamlit secrets
service_account_info = json.loads(st.secrets["gcp_service_account"])
creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)

# Google Sheet URL และชื่อ worksheet
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/edit"
worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

# ส่วนอินเทอร์เฟซ
st.title("📊 วิเคราะห์ตัวเลขทดสอบและชั่วโมงที่เหลือของ Brush")
st.subheader("📝 เพิ่มข้อมูลลง Sheet8 ที่เซลล์ H1 และ Brush Upper/Lower")

# กรอกจำนวนชั่วโมง
hours = st.number_input("กรอกจำนวนชั่วโมง", min_value=0.0, step=0.5)

# สร้างฟอร์มสำหรับ 32 ค่าของ Brush Upper และ Lower
st.markdown("🔺 **กรอกค่า Brush (2 ตัวแรกเป็น Upper / 2 ตัวหลังเป็น Lower)**")
upper_inputs = []
lower_inputs = []

cols_upper = st.columns(2)
for i in range(32):
    with cols_upper[i % 2]:
        upper_val = st.number_input(f"ตัวที่ {i + 1} (U)", key=f"upper_{i}", min_value=0.0)
        upper_inputs.append(upper_val)

cols_lower = st.columns(2)
for i in range(32):
    with cols_lower[i % 2]:
        lower_val = st.number_input(f"ตัวที่ {i + 1} (L)", key=f"lower_{i}", min_value=0.0)
        lower_inputs.append(lower_val)

if st.button("📝 บันทึกข้อมูลลง Sheet8"):
    try:
        worksheet.update("H1", [[hours]])
        for idx, val in enumerate(upper_inputs):
            cell = f"C{idx + 3}"
            worksheet.update(cell, [[val]])
        for idx, val in enumerate(lower_inputs):
            cell = f"F{idx + 3}"
            worksheet.update(cell, [[val]])
        st.success("✅ บันทึกข้อมูลสำเร็จ")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
