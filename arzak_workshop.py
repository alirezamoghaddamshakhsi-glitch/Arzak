import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")
st.title("🏗️ ARZAK Production")

# ۱. دریافت تنظیمات از Secrets
spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
# تبدیل متن JSON به دیکشنری برای استفاده در متد اتصال
service_account_info = json.loads(st.secrets["connections"]["gsheets"]["service_account"])

# ۲. ایجاد اتصال با هویت Service Account (برای اجازه نوشتن)
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # ۳. خواندن داده‌ها (استفاده از تنظیمات سرویس اکانت برای دسترسی کامل)
    df = conn.read(
        spreadsheet=spreadsheet_url,
        ttl=0
    )
    
    # تمیزکاری نام ستون‌ها
    df.columns = [str(c).strip() for c in df.columns]
    
    st.write("### Current Stock Levels")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.header("🔨 Report New Production")
    
    with st.form("production_form"):
        if 'Item' in df.columns and 'Color' in df.columns:
            item_list = df['Item'].unique().tolist()
            selected_item = st.selectbox("Product", item_list)
            
            color_list = df[df['Item'] == selected_item]['Color'].unique().tolist()
            selected_color = st.selectbox("Color", color_list)
            
            qty = st.number_input("Quantity Produced", min_value=1, step=1)
            
            if st.form_submit_button("Confirm & Update Cloud"):
                # عملیات آپدیت در حافظه برنامه
                mask = (df['Item'] == selected_item) & (df['Color'] == selected_color)
                if mask.any():
                    # تبدیل ستون Stock به عدد برای محاسبات
                    df['Stock'] = pd.to_numeric(df['Stock']).fillna(0)
                    df.loc[mask, 'Stock'] += qty
                    
                    # ۴. نوشتن در اکسل (اینجاست که Service Account لازم است)
                    conn.update(spreadsheet=spreadsheet_url, data=df)
                    
                    st.success(f"تعداد {qty} عدد به {selected_item} اضافه شد.")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("ترکیب کالا و رنگ یافت نشد.")
        else:
            st.error("خطا: ستون‌های Item و Color در فایل اکسل یافت نشدند.")

except Exception as e:
    st.error(f"خطای سیستمی: {e}")
