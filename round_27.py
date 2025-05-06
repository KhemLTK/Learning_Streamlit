
import streamlit as st
from google.oauth2.service_account import Credentials
import gspread

st.title("📊 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

st.subheader("📝 เพิ่มข้อมูลจำนวนชั่วโมงลง Sheet8")

# ป้อนค่าจำนวนชั่วโมง
input_hours = st.number_input("กรอกจำนวนชั่วโมง", min_value=0.0, format="%.2f")

# หากมีการกดปุ่ม
if st.button("เพิ่มข้อมูลจำนวนชั่วโมง"):
    try:
        # ใช้ค่า dict โดยตรงไม่ต้อง json.loads
        service_account_info = st.secrets["gcp_service_account"]

        # สร้าง credentials
        creds = Credentials.from_service_account_info(service_account_info)
        gc = gspread.authorize(creds)

        # เปิด sheet และเพิ่มข้อมูล
        sheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/edit"
        worksheet = gc.open_by_url(sheet_url).worksheet("Sheet8")
        worksheet.update("H1", str(input_hours))
        st.success(f"เพิ่มข้อมูลจำนวนชั่วโมง: {input_hours} ลง Sheet8 สำเร็จแล้ว")
    except Exception as e:
        st.error(f"โหลด credentials ไม่สำเร็จ: {e}")
