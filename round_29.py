import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")
st.subheader("📝 เพิ่มข้อมูลลง Sheet8 ที่เซลล์ H1 และ Brush Upper/Lower")

# อ่าน credentials จาก secrets
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)

# เปิดชีท
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/edit?usp=sharing"
worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

# ===== ฟอร์มกรอกข้อมูล =====
input_hours = st.number_input("⏱️ กรอกจำนวนชั่วโมง", min_value=0.0, step=0.1)

st.markdown("### 🔺 กรอกค่า Brush Upper (32 ค่า)")
upper_values = []
cols_upper = st.columns(4)
for i in range(32):
    with cols_upper[i % 4]:
        val = st.number_input(f"U{i+1}", key=f"upper_{i}", value=0.0, step=0.01)
        upper_values.append(val)

st.markdown("### 🔻 กรอกค่า Brush Lower (32 ค่า)")
lower_values = []
cols_lower = st.columns(4)
for i in range(32):
    with cols_lower[i % 4]:
        val = st.number_input(f"L{i+1}", key=f"lower_{i}", value=0.0, step=0.01)
        lower_values.append(val)

# ===== ปุ่มและการบันทึก =====
if st.button("➕ เพิ่มข้อมูลทั้งหมด"):
    try:
        # บันทึก H1 เป็นจำนวนชั่วโมง
        worksheet.update("H1", [[input_hours]])

        # บันทึก Brush Upper ที่แถว 2 (A2 - AF2)
        worksheet.update("A2:AF2", [upper_values])

        # บันทึก Brush Lower ที่แถว 3 (A3 - AF3)
        worksheet.update("A3:AF3", [lower_values])

        st.success("✅ บันทึกข้อมูลทั้งหมดสำเร็จ")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")