import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")
st.title("🏗️ ARZAK Production")

# روش جدید برای جلوگیری از ارور Multiple Values
try:
    # ۱. استخراج اطلاعات از Secrets
    secret_data = json.loads(st.secrets["connections"]["gsheets"]["service_account"])
    
    # ۲. حذف کلید type از دیکشنری برای جلوگیری از تداخل با متد داخلی Streamlit
    if "type" in secret_data:
        del secret_data["type"]
    
    # ۳. ایجاد اتصال بدون فرستادن کلمه کلیدی type به صورت دستی
    conn = st.connection("gsheets", type=GSheetsConnection, **secret_data)
    
    # ۴. خواندن اطلاعات
    df = conn.read(worksheet="Inventory", ttl=0)
    df['Stock'] = pd.to_numeric(df['Stock']).fillna(0)
    
    st.write("### Current Stock Levels")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.header("🔨 Report New Production")
    
    with st.form("production_form"):
        items = df['Item'].unique().tolist()
        item = st.selectbox("Product", items)
        colors = df[df['Item'] == item]['Color'].unique().tolist()
        color = st.selectbox("Color", colors)
        qty = st.number_input("Quantity Produced", min_value=1, step=1)
        
        if st.form_submit_button("Confirm & Update Cloud"):
            mask = (df['Item'] == item) & (df['Color'] == color)
            if mask.any():
                df.loc[mask, 'Stock'] += qty
                conn.update(worksheet="Inventory", data=df)
                st.success("Cloud Updated Successfully!")
                st.balloons()
                st.rerun()
            else:
                st.warning("Combination not found in Excel.")

except Exception as e:
    st.error(f"خطا در اتصال: {e}")
    st.info("نکته: مطمئن شوید ایمیل سرویس اکانت در گوگل شیت Editor است.")
