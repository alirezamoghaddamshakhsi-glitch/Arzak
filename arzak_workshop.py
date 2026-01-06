import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")
st.title("🏗️ ARZAK Production")

# تابع کمکی برای استخراج ID از لینک گوگل شیت
def get_spreadsheet_id(url):
    try:
        if "/d/" in url:
            return url.split("/d/")[1].split("/")[0]
        return url
    except:
        return url

try:
    # ۱. فراخوانی لینک از Secrets
    full_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = get_spreadsheet_id(full_url)
    
    # ۲. ایجاد اتصال
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # ۳. خواندن دیتا - از نام برگه "Inventory" استفاده می‌کنیم
    # اگر نام برگه شما چیزی غیر از Inventory است، اینجا عوضش کنید
    df = conn.read(
        spreadsheet=sheet_id,
        worksheet="Inventory",
        ttl=0
    )
    
    # پاکسازی دیتا
    df.columns = df.columns.str.strip() # حذف فاصله‌های اضافه از نام ستون‌ها
    df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0)
    
    st.write("### Current Stock Levels")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.header("🔨 Report New Production")
    
    with st.form("production_form"):
        item_list = df['Item'].unique().tolist()
        selected_item = st.selectbox("Product", item_list)
        
        available_colors = df[df['Item'] == selected_item]['Color'].unique().tolist()
        selected_color = st.selectbox("Color", available_colors)
        
        qty = st.number_input("Quantity Produced", min_value=1, step=1)
        
        if st.form_submit_button("Confirm & Update"):
            mask = (df['Item'] == selected_item) & (df['Color'] == selected_color)
            if mask.any():
                df.loc[mask, 'Stock'] += qty
                conn.update(spreadsheet=sheet_id, worksheet="Inventory", data=df)
                st.success("Cloud Updated!")
                st.balloons()
                st.rerun()
            else:
                st.warning("Combination not found.")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("💡 چک‌لیست نهایی برای حل ارور 400:")
    st.write("1. مطمئن شوید نام برگه در پایین اکسل دقیقاً **Inventory** است (بدون فاصله اضافه).")
    st.write("2. در Secrets، مطمئن شوید لینک `spreadsheet` بین دو کوتیشن است.")
    st.write("3. ستون‌های اکسل باید دقیقاً اینها باشند: **Item**, **Color**, **Stock**, **UnitCost**")
