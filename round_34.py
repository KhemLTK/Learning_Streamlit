
import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Brush Entry to Google Sheet", layout="wide")

st.title("📊 วิเคราะห์ตัวเลขทดสอบแปรงถ่าน")

st.header("📝 เพิ่มข้อมูลลง Sheet8 ที่เซลล์ H1 และ Brush Upper/Lower")

# กรอกจำนวนชั่วโมง
hours = st.number_input("🕒 กรอกจำนวนชั่วโมง", min_value=0.0, step=1.0)

# กรอกค่าของ Brush Upper (32 ค่า)
st.subheader("🔺 กรอกค่า Brush Upper (32 ค่า)")
cols_upper = st.columns(4)
upper_values = []
for i in range(32):
    with cols_upper[i % 4]:
        val = st.number_input(f"ตัวที่ {i + 1} (U)", key=f"upper_{i}")
        upper_values.append(val)

# กรอกค่าของ Brush Lower (32 ค่า)
st.subheader("🔻 กรอกค่า Brush Lower (32 ค่า)")
cols_lower = st.columns(4)
lower_values = []
for i in range(32):
    with cols_lower[i % 4]:
        val = st.number_input(f"ตัวที่ {i + 1} (L)", key=f"lower_{i}")
        lower_values.append(val)

# โหลด credentials จาก secrets
try:
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info)
    gc = gspread.authorize(creds)

    # URL ของ Google Sheet
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/edit"
    worksheet = gc.open_by_url(spreadsheet_url).worksheet("Sheet8")

    if st.button("📥 บันทึกข้อมูลลง Google Sheet"):
        try:
            worksheet.update("H1", [[hours]])
            for i in range(32):
                worksheet.update(f"C{i+3}", [[upper_values[i]]])
                worksheet.update(f"F{i+3}", [[lower_values[i]]])
            st.success("✅ บันทึกข้อมูลสำเร็จแล้ว")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

except Exception as e:
    st.error(f"โหลด credentials ไม่สำเร็จ: {e}")
