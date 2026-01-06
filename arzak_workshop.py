import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")
st.title("🏗️ ARZAK Production")

# اتصال امن با استفاده از Service Account
try:
    # پارس کردن متن JSON از Secrets
    service_info = json.loads(st.secrets["connections"]["gsheets"]["service_account"])
    conn = st.connection("gsheets", type=GSheetsConnection, **service_info)
    
    # خواندن اطلاعات از برگه Inventory
    df = conn.read(worksheet="Inventory", ttl=0)
    
    # اصلاح فرمت اعداد
    df['Stock'] = pd.to_numeric(df['Stock']).fillna(0)
    
    st.write("### Current Stock Levels")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.header("🔨 Report New Production")
    
    with st.form("production_form"):
        # انتخاب کالا و رنگ بر اساس دیتای موجود در اکسل
        items = df['Item'].unique().tolist()
        item = st.selectbox("Product", items)
        colors = df[df['Item'] == item]['Color'].unique().tolist()
        color = st.selectbox("Color", colors)
        qty = st.number_input("Quantity Produced", min_value=1, step=1)
        
        if st.form_submit_button("Confirm & Update Cloud"):
            mask = (df['Item'] == item) & (df['Color'] == color)
            if mask.any():
                df.loc[mask, 'Stock'] += qty
                # ارسال آپدیت به گوگل شیت
                conn.update(worksheet="Inventory", data=df)
                st.success("انبار با موفقیت آپدیت شد!")
                st.balloons()
                st.rerun()
            else:
                st.warning("کالا یا رنگ انتخاب شده در جدول یافت نشد.")

except Exception as e:
    st.error(f"خطا در اتصال: {e}")
    st.info("نکته: حتماً ایمیل سرویس اکانت را در گوگل شیت Editor کنید.")
