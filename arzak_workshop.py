import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")
st.title("🏗️ ARZAK Production")

# رفع خطای Multiple Values برای پارامتر type
try:
    # ۱. استخراج تنظیمات از Secrets
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    service_info = json.loads(st.secrets["connections"]["gsheets"]["service_account"])
    
    # ۲. حذف کلید type از دیکشنری JSON برای جلوگیری از تداخل با متد داخلی Streamlit
    if "type" in service_info:
        del service_info["type"]
    
    # ۳. ایجاد اتصال با هویت Service Account
    # حالا دیگر تداخلی بین type داخل JSON و type تعریف شده در اینجا وجود ندارد
    conn = st.connection("gsheets", type=GSheetsConnection, **service_info)
    
    # ۴. خواندن داده‌ها
    df = conn.read(spreadsheet=spreadsheet_url, ttl=0)
    
    # تمیزکاری نام ستون‌ها و تبدیل فرمت اعداد
    df.columns = [str(c).strip() for c in df.columns]
    if 'Stock' in df.columns:
        df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0)
    
    st.write("### Current Stock Levels")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.header("🔨 Report New Production")
    
    with st.form("production_form"):
        if 'Item' in df.columns and 'Color' in df.columns:
            items = df['Item'].unique().tolist()
            selected_item = st.selectbox("Product", items)
            
            colors = df[df['Item'] == selected_item]['Color'].unique().tolist()
            selected_color = st.selectbox("Color", colors)
            
            qty = st.number_input("Quantity Produced", min_value=1, step=1)
            
            if st.form_submit_button("Confirm & Update Cloud"):
                mask = (df['Item'] == selected_item) & (df['Color'] == selected_color)
                if mask.any():
                    df.loc[mask, 'Stock'] += qty
                    
                    # ۵. ارسال آپدیت به گوگل شیت
                    conn.update(spreadsheet=spreadsheet_url, data=df)
                    
                    st.success(f"موجودی {selected_item} با موفقیت به‌روزرسانی شد.")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("این ترکیب کالا و رنگ یافت نشد.")
        else:
            st.error("ستون‌های Item یا Color در اکسل پیدا نشدند.")

except Exception as e:
    st.error(f"خطای سیستمی: {e}")
    st.info("نکته: مطمئن شوید ایمیل سرویس اکانت در گوگل شیت Editor است.")
