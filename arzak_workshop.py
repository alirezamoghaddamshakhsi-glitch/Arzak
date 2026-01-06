import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")

st.title("🏗️ ARZAK Production")
st.subheader("Workshop Management Terminal")

# ایجاد اتصال به گوگل شیت
conn = st.connection("gsheets", type=GSheetsConnection)

# --- نمایش موجودی لحظه‌ای ---
try:
    # خواندن دیتا از شیت Inventory
    df = conn.read(worksheet="Inventory", ttl=0) # ttl=0 یعنی همیشه جدیدترین دیتا را بگیر
    st.write("### Current Stock Levels")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error("Error loading data. Check your Google Sheet name and sharing settings.")

st.markdown("---")

# --- فرم ثبت تولید جدید ---
st.header("🔨 Report New Production")
with st.form("production_form"):
    # گرفتن لیست محصولات از خودِ اکسل (برای داینامیک بودن)
    items_list = df['Item'].unique().tolist() if 'df' in locals() else ["Shelf 50x16"]
    
    selected_item = st.selectbox("Product", items_list)
    selected_color = st.selectbox("Color", ["White", "Black", "Gray", "Brown"])
    qty_produced = st.number_input("Quantity Built", min_value=1, step=1)
    
    submit_button = st.form_submit_button("Confirm & Update Cloud")

    if submit_button:
        try:
            # پیدا کردن ردیف مورد نظر و اضافه کردن تعداد تولید شده به موجودی قبلی
            mask = (df['Item'] == selected_item) & (df['Color'] == selected_color)
            
            if mask.any():
                df.loc[mask, 'Stock'] = df.loc[mask, 'Stock'].fillna(0) + qty_produced
                # آپدیت کردن کل شیت
                conn.update(worksheet="Inventory", data=df)
                st.success(f"Updated! {qty_produced} units added to {selected_item} ({selected_color}).")
                st.balloons()
            else:
                st.warning("This combination of Item and Color was not found in your Excel. Add it manually first.")
        except Exception as e:
            st.error(f"Could not update: {e}")

st.caption("Tip: Refresh page to see updated stock.")
