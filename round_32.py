import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")
st.subheader("📝 เพิ่มข้อมูลจำนวนชั่วโมง + Brush Upper/Lower 32 ตัว")

# ✅ Load credentials
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)

# ✅ Open Sheet8
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/edit?usp=sharing"
worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

# ✅ Input ชั่วโมง
input_hours = st.number_input("⏱️ กรอกจำนวนชั่วโมง", min_value=0.0, step=0.1)

# ✅ กรอกค่า Upper และ Lower อย่างละ 32 ช่อง
st.markdown("### 🔺 กรอกค่า Brush Upper (32 ค่า)")
upper_values = [st.number_input(f"ตัวที่ {i+1}", key=f"upper_{i}", step=0.01, min_value=0.0) for i in range(32)]

st.markdown("### 🔻 กรอกค่า Brush Lower (32 ค่า)")
lower_values = [st.number_input(f"ตัวที่ {i+1}", key=f"lower_{i}", step=0.01, min_value=0.0) for i in range(32)]

# ✅ บันทึกข้อมูลทั้งหมด
if st.button("📤 บันทึกข้อมูลทั้งหมด"):
    try:
        # ชั่วโมง -> H1
        worksheet.update("H1", [[input_hours]])

        # Upper -> C3 to C34 (column 3)
        worksheet.update("C3:C34", [[v] for v in upper_values])

        # Lower -> F3 to F34 (column 6)
        worksheet.update("F3:F34", [[v] for v in lower_values])

        st.success("✅ บันทึกข้อมูลสำเร็จแล้วทั้งหมด")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")