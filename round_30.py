
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
