import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")
st.title("🏗️ ARZAK Production")

# استفاده از ساختار ساده‌تر برای رفع ارور 400
try:
    # ۱. اتصال پایه
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # ۲. خواندن دیتا با آدرس مستقیم (این روش در برابر Bad Request مقاوم‌تر است)
    # حتماً لینک شیت را در Secrets چک کنید که دقیق باشد
    df = conn.read(
        spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"],
        worksheet="Inventory",
        ttl=0
    )
    
    # ۳. آماده‌سازی اعداد
    df['Stock'] = pd.to_numeric(df['Stock']).fillna(0)
    
    st.write("### Current Stock Levels")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.header("🔨 Report New Production")
    
    with st.form("production_form"):
        items = df['Item'].unique().tolist()
        selected_item = st.selectbox("Product", items)
        
        # فیلتر رنگ‌ها بر اساس محصول انتخاب شده
        available_colors = df[df['Item'] == selected_item]['Color'].unique().tolist()
        selected_color = st.selectbox("Color", available_colors)
        
        qty = st.number_input("Quantity Produced", min_value=1, step=1)
        
        if st.form_submit_button("Confirm & Update Cloud"):
            mask = (df['Item'] == selected_item) & (df['Color'] == selected_color)
            if mask.any():
                df.loc[mask, 'Stock'] += qty
                # آپدیت کردن فایل
                conn.update(
                    spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"],
                    worksheet="Inventory",
                    data=df
                )
                st.success("انبار با موفقیت به‌روزرسانی شد!")
                st.balloons()
                st.rerun()
            else:
                st.warning("این ترکیب محصول و رنگ در جدول یافت نشد.")

except Exception as e:
    st.error(f"خطا در اتصال: {e}")
    st.info("نکته مهم: مطمئن شوید نام برگه در اکسل دقیقاً Inventory است (با I بزرگ).")
