
import streamlit as st

# Input: Operating Hours
st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")
st.subheader("📝 เพิ่มข้อมูลลง Sheet8 ที่เซลล์ H1 และ Brush Upper/Lower")

hours = st.number_input("กรอกจำนวนชั่วโมง", min_value=0.0, step=1.0)

st.markdown("### 🔺 กรอกค่า Brush (2 ตัวแรกเป็น Upper / 2 ตัวหลังเป็น Lower)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    brush_u1 = st.number_input("ตัวที่1", key="u1")
    brush_u2 = st.number_input("ตัวที่2", key="u2")
with col2:
    brush_l1 = st.number_input("ตัวที่3", key="l1")
    brush_l2 = st.number_input("ตัวที่4", key="l2")

# Display collected values
if st.button("✅ เพิ่มข้อมูลแปรง"):
    st.success(f"เพิ่มข้อมูลสำเร็จ:\nชั่วโมง = {hours}\nUpper = {[brush_u1, brush_u2]}\nLower = {[brush_l1, brush_l2]}")



# ✅ ส่วนเชื่อมต่อ Google Sheets และเพิ่มข้อมูลในตำแหน่งที่กำหนด
import json
import gspread
from google.oauth2.service_account import Credentials

st.subheader("📤 เพิ่มข้อมูลลง Google Sheet")

if st.button("✅ บันทึกข้อมูลลง Sheet8"):
    try:
        # ดึงข้อมูล credentials จาก Streamlit secrets
        service_account_info = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(creds)

        # เปิด Sheet8 ด้วย URL และดึง Worksheet
        spreadsheet_url = st.secrets["spreadsheet_url"]
        worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

        # เตรียมข้อมูลที่ต้องการใส่
        for i in range(32):
            worksheet.update_cell(i + 3, 3, upper_values[i])  # C3 ถึง C34
            worksheet.update_cell(i + 3, 6, lower_values[i])  # F3 ถึง F34

        st.success("✅ บันทึกข้อมูลเรียบร้อยแล้วลง Sheet8 ในตำแหน่ง C3:C34 และ F3:F34")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
