import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")

st.title("🏗️ ARZAK Production")
st.subheader("Workshop Management Terminal")

# Connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- DISPLAY CURRENT STOCK ---
st.write("### Current Stock Levels")
data = conn.read(worksheet="Inventory")
st.dataframe(data, use_container_width=True)

st.markdown("---")

# --- REPORT PRODUCTION ---
st.header("🔨 Report New Production")
with st.form("production_form"):
    item = st.selectbox("Product", ["Shelf 50x16", "Wall Panel"])
    color = st.selectbox("Color", ["White", "Black", "Gray", "Brown"])
    qty = st.number_input("Quantity Built", min_value=1, step=1)
    
    if st.form_submit_button("Confirm Production"):
        # Logic: In a real app, this would update the Google Sheet row
        st.success(f"Production recorded! {qty} {color} {item} added to inventory.")
        st.balloons()

# --- AUDIT (THURSDAY 8:00 AM) ---
st.header("🔍 Manual Audit")
with st.expander("Update component count manually"):
    comp = st.selectbox("Component", ["Wooden Leg", "Screw", "Packaging"])
    actual_count = st.number_input("Actual Count in Workshop", min_value=0)
    if st.button("Sync Audit"):
        st.warning(f"Audit Complete: {comp} set to {actual_count}")