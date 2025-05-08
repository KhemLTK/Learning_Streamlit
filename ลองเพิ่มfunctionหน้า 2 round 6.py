
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Brush Dashboard", layout="wide")

page = st.sidebar.radio("📂 เลือกหน้า", [
    "📝 กรอกข้อมูลแปลงถ่านเพิ่มเติม",
])

if page == "📝 กรอกข้อมูลแปลงถ่านเพิ่มเติม":
    st.title("📝 กรอกข้อมูลแปรงถ่าน + ชั่วโมง")

    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1SOkIH9jchaJi_0eck5UeyUR8sTn2arndQofmXv5pTdQ")

    editable_sheets = [ws.title for ws in sh.worksheets() if "Sheet" in ws.title]
    selected_sheet = st.selectbox("📄 เลือก Sheet ที่ต้องการกรอกข้อมูล", editable_sheets)
    ws = sh.worksheet(selected_sheet)

    hours = st.number_input("⏱️ ชั่วโมง", min_value=0.0, step=0.1)

    st.markdown("### 🔧 แปลงถ่านส่วน UPPER")
    upper = []
    cols = st.columns(8)
    for i in range(32):
        col = cols[i % 8]
        with col:
            value = st.text_input(f"{i+1}", key=f"u{i}", label_visibility="collapsed", placeholder="0.00")
            try:
                upper.append(float(value))
            except:
                upper.append(0.0)

    st.markdown("### 🔧 แปลงถ่านส่วน LOWER")
    lower = []
    cols = st.columns(8)
    for i in range(32):
        col = cols[i % 8]
        with col:
            value = st.text_input(f"{i+1}", key=f"l{i}", label_visibility="collapsed", placeholder="0.00")
            try:
                lower.append(float(value))
            except:
                lower.append(0.0)

    if st.button("📤 บันทึก"):
        try:
            ws.update("H1", [[hours]])
            ws.update("C3:C34", [[v] for v in upper])
            ws.update("F3:F34", [[v] for v in lower])
            st.success(f"✅ บันทึกลง {selected_sheet} แล้วเรียบร้อย")
        except Exception as e:
            st.error(f"❌ {e}")

    
)),
                                 mode='lines+markers', name='Lower Current', line=dict(dash='dot')))
        fig.add_trace(go.Scatter(y=lower_df["Lower_Previous"], x=list(range(1, len(lower_df)+1)),
                                 mode='lines+markers', name='Lower Previous', line=dict(dash='dot')))
        fig.update_layout(xaxis_title='Brush Number', yaxis_title='mm', height=600)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"❌ ไม่สามารถโหลดข้อมูลจากชีตนี้ได้: {e}")
