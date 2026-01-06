import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")
st.title("🏗️ ARZAK Production")

# رفع ارور Multiple Values با حذف پارامتر تکراری
try:
    # لود کردن تنظیمات از Secrets
    service_info = json.loads(st.secrets["connections"]["gsheets"]["service_account"])
    
    # اینجا GSheetsConnection را مستقیماً به عنوان اولین آرگومان می‌فرستیم
    # و دیگر از کلمه کلیدی type= استفاده نمی‌کنیم
    conn = st.connection("gsheets", GSheetsConnection, **service_info)
    
    # لود کردن داده‌ها
    df = conn.read(worksheet="Inventory", ttl=0)
    df['Stock'] = pd.to_numeric(df['Stock']).fillna(0)
    
    st.write("### Current Stock Levels")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.header("🔨 Report New Production")
    
    with st.form("production_form"):
        item_list = df['Item'].unique().tolist()
        item = st.selectbox("Product", item_list)
        color_list = df[df['Item'] == item]['Color'].unique().tolist()
        color = st.selectbox("Color", color_list)
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
    st.info("نکته: مطمئن شوید متن JSON در Secrets بین سه کوتیشن ''' قرار دارد.")
