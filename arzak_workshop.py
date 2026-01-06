import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")
st.title("🏗️ ARZAK Production")

# ۱. استخراج تنظیمات از Secrets با دقت بالا
try:
    # خواندن لینک شیت
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # تبدیل رشته JSON به دیکشنری پایتون
    service_info = json.loads(st.secrets["connections"]["gsheets"]["service_account"])
    
    # ۲. ایجاد اتصال - ارسال مستقیم تنظیمات سرویس اکانت
    # این خط به کتابخانه می‌گوید که ما اجازه ویرایش (Write) داریم
    conn = st.connection("gsheets", type=GSheetsConnection, **service_info)
    
    # ۳. خواندن داده‌ها
    df = conn.read(spreadsheet=spreadsheet_url, ttl=0)
    
    # تمیزکاری داده‌ها
    df.columns = [str(c).strip() for c in df.columns]
    df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0)
    
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
                # آپدیت در حافظه
                mask = (df['Item'] == selected_item) & (df['Color'] == selected_color)
                if mask.any():
                    df.loc[mask, 'Stock'] += qty
                    
                    # ۴. ارسال آپدیت به گوگل شیت (با استفاده از کلیدهای امنیتی)
                    conn.update(spreadsheet=spreadsheet_url, data=df)
                    
                    st.success(f"موجودی {selected_item} ({selected_color}) با موفقیت آپدیت شد.")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("این کالا در لیست یافت نشد.")
        else:
            st.error("سرتیترهای Item و Color در اکسل یافت نشدند.")

except Exception as e:
    st.error(f"خطای سیستمی: {e}")
    st.info("نکته: مطمئن شوید ایمیل سرویس اکانت در گوگل شیت Editor است.")
