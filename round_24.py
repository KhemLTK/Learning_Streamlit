
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime
import json
import os

# โหลด credentials จาก secrets ของ Streamlit
service_account_info = json.loads(st.secrets["gcp_service_account"])
creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

# เปิด Google Sheet
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ"
spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]

gc = gspread.authorize(creds)
sh = gc.open_by_key(spreadsheet_id)

# UI
st.title("🛠 วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

# ปุ่มเพิ่มข้อมูลแปลงถ่าน
if st.button("➕ เพิ่มข้อมูลแปลงถ่าน"):
    input_hour = st.number_input("กรอกจำนวนชั่วโมง", min_value=0.0, step=0.1)
    if st.button("📥 ยืนยันเพิ่มข้อมูล"):
        try:
            sheet8 = sh.worksheet("Sheet8")
            last_row = len(sheet8.col_values(1)) + 1
            sheet8.update_acell(f"H{last_row}", str(input_hour))
            st.success(f"เพิ่มข้อมูลสำเร็จ: {input_hour} ไปยัง Sheet8 ช่อง H{last_row}")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
