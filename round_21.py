
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIG --- #
SHEET_NAME = "Sheet8"
COLUMN = "H"

# --- AUTHENTICATION --- #
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# --- CONNECT TO SHEET --- #
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ"
spreadsheet = client.open_by_url(spreadsheet_url)
worksheet = spreadsheet.worksheet(SHEET_NAME)

# --- UI --- #
st.markdown("## ➕ เพิ่มข้อมูลแปรงถ่าน")
st.write("กรอกจำนวนชั่วโมงที่ต้องการเพิ่มไปยัง Sheet8 คอลัมน์ 1H")

input_hours = st.number_input("จำนวนชั่วโมง (ตัวเลขเท่านั้น)", min_value=0.0, step=0.5)

if st.button("📥 เพิ่มข้อมูลแปรงถ่าน"):
    try:
        last_row = len(worksheet.col_values(8)) + 1  # column H = 8
        worksheet.update_acell(f"{COLUMN}{last_row}", str(input_hours))
        st.success(f"เพิ่มข้อมูล {input_hours} ชั่วโมง ไปยังช่อง {COLUMN}{last_row} ใน Sheet8 สำเร็จแล้ว ✅")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเพิ่มข้อมูล: {e}")
