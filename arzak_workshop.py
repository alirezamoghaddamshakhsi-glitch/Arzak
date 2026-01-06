import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")

st.title("🏗️ ARZAK Production")
st.subheader("Workshop Management Terminal")

# ایجاد اتصال به گوگل شیت
conn = st.connection("gsheets", type=GSheetsConnection)

# تابع کمکی برای خواندن دیتا (برای جلوگیری از گم شدن df)
def load_data():
    return conn.read(worksheet="Inventory", ttl=0)

# خواندن دیتای اولیه
df = load_data()

# --- نمایش موجودی ---
st.write("### Current Stock Levels")
if df is not None:
    # پر کردن مقادیر None با صفر برای جلوگیری از ارور محاسباتی
    df['Stock'] = df['Stock'].fillna(0)
    st.dataframe(df, use_container_width=True)

st.markdown("---")

# --- فرم ثبت تولید جدید ---
st.header("🔨 Report New Production")
with st.form("production_form"):
    # لیست محصولات از ستون Item در اکسل
    items_list = df['Item'].unique().tolist() if df is not None else ["Shelf 50x16"]
    
    selected_item = st.selectbox("Product", items_list)
    selected_color = st.selectbox("Color", ["White", "Black", "Gray", "Brown"])
    qty_produced = st.number_input("Quantity Built", min_value=1, step=1)
    
    submit_button = st.form_submit_button("Confirm & Update Cloud")

    if submit_button:
        try:
            # آپدیت ردیف مورد نظر
            mask = (df['Item'] == selected_item) & (df['Color'] == selected_color)
            
            if mask.any():
                # اضافه کردن به موجودی فعلی
                df.loc[mask, 'Stock'] = df.loc[mask, 'Stock'].astype(float) + qty_produced
                
                # ارسال کل جدول به گوگل شیت
                conn.update(worksheet="Inventory", data=df)
                st.success(f"Updated! {qty_produced} units added to {selected_item}.")
                st.balloons()
                # رفرش کردن دیتا برای نمایش جدید
                st.rerun()
            else:
                st.warning("This Item/Color combination was not found in Excel.")
        except Exception as e:
            st.error(f"Update failed: {e}")

st.caption("Tip: Refresh page to see updated stock.")
