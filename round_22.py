
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# เชื่อมต่อ Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
gc = gspread.authorize(CREDS)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ"
spreadsheet = gc.open_by_url(SHEET_URL)

st.title("🛠️ วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

# ฟังก์ชันดึงข้อมูลจาก Google Sheet
@st.cache_data
def load_sheet(sheet_index):
    worksheet = spreadsheet.get_worksheet(sheet_index)
    df = pd.DataFrame(worksheet.get_all_records())
    return df

# ======================= Display Existing Data ============================
selected_sheet = st.number_input("📌 เลือกหมายเลข Sheet ที่ต้องการใช้ (สำหรับคำนวณ Avg Rate)", min_value=0, max_value=10, value=7)
df = load_sheet(selected_sheet)
st.subheader("📋 ตัวอย่างข้อมูลจาก Google Sheet")
st.dataframe(df.head())

# ======================= เพิ่มข้อมูลใหม่เข้า Sheet8 ========================
st.markdown("---")
st.markdown("### ➕ ต้องการเพิ่มข้อมูลแปรงถ่านไหม")
if st.button("เพิ่มข้อมูลแปรงถ่าน"):
    input_hour = st.number_input("กรอกจำนวนชั่วโมง (mm):", min_value=0.0, step=0.1)
    if st.button("บันทึกข้อมูล"):
        try:
            worksheet8 = spreadsheet.worksheet("Sheet8")
            worksheet8.update("H1", [[input_hour]])  # เพิ่มข้อมูลในช่อง H1
            st.success(f"✅ เพิ่มข้อมูลสำเร็จ: {input_hour} mm")
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")
