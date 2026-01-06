import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")
st.title("🏗️ ARZAK Production")

# ۱. ایجاد اتصال پایه
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # ۲. خواندن داده‌ها با استفاده از لینک مستقیم (URL) 
    # این روش معمولاً ارور 400 را دور می‌زند
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # خواندن کل شیت (بدون مشخص کردن نام Worksheet در ابتدا برای تست)
    df = conn.read(spreadsheet=spreadsheet_url, ttl=0)
    
    # اگر ستون‌ها پیدا نشدند یا نام برگه اشتباه بود، به کاربر هشدار بده
    if df is not None:
        # پاکسازی نام ستون‌ها (حذف فضاهای خالی)
        df.columns = [str(c).strip() for c in df.columns]
        
        st.write("### Current Stock Levels")
        st.dataframe(df, use_container_width=True)
    else:
        st.error("No data found in the spreadsheet.")
        st.stop()

    st.markdown("---")
    st.header("🔨 Report New Production")
    
    with st.form("production_form"):
        # چک کردن وجود ستون‌های حیاتی
        if 'Item' in df.columns and 'Color' in df.columns:
            item_list = df['Item'].unique().tolist()
            selected_item = st.selectbox("Product", item_list)
            
            color_list = df[df['Item'] == selected_item]['Color'].unique().tolist()
            selected_color = st.selectbox("Color", color_list)
            
            qty = st.number_input("Quantity Produced", min_value=1, step=1)
            
            if st.form_submit_button("Confirm & Update"):
                # عملیات آپدیت
                mask = (df['Item'] == selected_item) & (df['Color'] == selected_color)
                if mask.any():
                    df.loc[mask, 'Stock'] = pd.to_numeric(df.loc[mask, 'Stock']).fillna(0) + qty
                    conn.update(spreadsheet=spreadsheet_url, data=df)
                    st.success("Cloud Updated!")
                    st.balloons()
                    st.rerun()
        else:
            st.warning("ستون‌های Item یا Color پیدا نشدند. نام سرتیترهای اکسل را چک کنید.")

except Exception as e:
    st.error(f"اتصال ناموفق: {e}")
    st.info("راه حل احتمالی: در فایل اکسل، نام اولین برگه را از Inventory به Sheet1 تغییر بده و تست کن.")
