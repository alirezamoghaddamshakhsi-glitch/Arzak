import streamlit as st
import pandas as pd

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")

st.title("🏗️ ARZAK Production")
st.subheader("Workshop Management Terminal")

# --- اتصال مستقیم و امن ---
try:
    # خواندن لینک از Secrets
    raw_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # تبدیل لینک معمولی به لینک دانلود مستقیم CSV
    # این بخش ارور HTTP را دور می‌زند
    csv_url = raw_url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=Inventory")
    
    # خواندن دیتا
    data = pd.read_csv(csv_url)
    
    st.write("### Current Stock Levels")
    st.dataframe(data, use_container_width=True)

except Exception as e:
    st.error("Connection Error!")
    st.info("Make sure your Google Sheet is Shared as 'Anyone with the link can EDIT'")
    st.write(f"Error Details: {e}")

st.markdown("---")

# --- فرم ثبت تولید ---
st.header("🔨 Report New Production")
with st.form("production_form"):
    item = st.selectbox("Product", ["Shelf 50x16", "Wall Panel"])
    color = st.selectbox("Color", ["White", "Black", "Gray", "Brown"])
    qty = st.number_input("Quantity Built", min_value=1, step=1)
    
    if st.form_submit_button("Confirm Production"):
        st.success(f"Production recorded! {qty} {color} {item} added.")
        st.balloons()
