
import streamlit as st
import pandas as pd

# Set Streamlit page config
st.set_page_config(page_title="วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush", layout="wide")

st.title("🛠️ วิเคราะห์อัตราสึกหรอและชั่วโมงที่เหลือของ Brush")

# Load Google Sheet as CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ/edit?usp=sharing"
csv_url = sheet_url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv")

try:
    xls = pd.read_csv(csv_url)
    st.success("โหลดข้อมูลจาก Google Sheet สำเร็จแล้ว ✅")
    st.dataframe(xls)
except Exception as e:
    st.error(f"ไม่สามารถโหลดข้อมูลจาก Google Sheets ได้: {e}")
