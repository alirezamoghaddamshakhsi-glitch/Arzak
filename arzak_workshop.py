import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")
st.title("🏗️ ARZAK Production")

# روش نهایی برای رفع تداخل پارامترها (مثل project_id)
try:
    # ۱. خواندن اطلاعات از Secrets
    service_info = json.loads(st.secrets["connections"]["gsheets"]["service_account"])
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # ۲. ایجاد اتصال با متد صحیح
    # در این حالت ما تنظیمات را مستقیماً به کلاینت داخلی می‌فرستیم
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # ۳. خواندن اطلاعات با استفاده از لینک مستقیم (برای دور زدن محدودیت‌های متد قبلی)
    df = conn.read(
        spreadsheet=spreadsheet_url,
        worksheet="Inventory",
        ttl=0
    )
    
    # اصلاح فرمت اعداد
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
                # آپدیت در گوگل شیت
                conn.update(spreadsheet=spreadsheet_url, worksheet="Inventory", data=df)
                st.success("Successfully Updated!")
                st.balloons()
                st.rerun()
            else:
                st.warning("Combination not found in Excel.")

except Exception as e:
    st.error(f"خطا در اتصال: {e}")
    st.info("نکته: مطمئن شوید ایمیل سرویس اکانت در گوگل شیت Editor است.")
