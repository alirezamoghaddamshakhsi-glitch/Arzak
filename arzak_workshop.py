import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

st.set_page_config(page_title="ARZAK Workshop", page_icon="🏗️")

st.title("🏗️ ARZAK Production")
st.subheader("Workshop Management Terminal")

# --- اتصال فوق‌امن و بدون تداخل ---
try:
    # ۱. خواندن مشخصات از Secrets
    ss_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    service_info = json.loads(st.secrets["connections"]["gsheets"]["service_account"])
    
    # ۲. حذف کلید مزاحم برای جلوگیری از ارور Multiple Values
    if "type" in service_info:
        del service_info["type"]
    
    # ۳. برقرار اتصال با متد تمیز
    conn = st.connection("gsheets", type=GSheetsConnection, **service_info)
    
    # ۴. خواندن دیتا
    df = conn.read(spreadsheet=ss_url, ttl=0)
    
    # تمیزکاری نام ستون‌ها و اعداد
    df.columns = [str(c).strip() for c in df.columns]
    if 'Stock' in df.columns:
        df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0)
    
    # نمایش جدول
    st.write("### موجودی فعلی انبار")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # --- فرم ثبت تولید ---
    st.header("🔨 ثبت گزارش تولید جدید")
    with st.form("production_form"):
        if 'Item' in df.columns and 'Color' in df.columns:
            items = df['Item'].unique().tolist()
            selected_item = st.selectbox("نام محصول", items)
            
            colors = df[df['Item'] == selected_item]['Color'].unique().tolist()
            selected_color = st.selectbox("رنگ", colors)
            
            qty = st.number_input("تعداد تولید شده", min_value=1, step=1)
            
            if st.form_submit_button("تایید و ثبت در سیستم"):
                mask = (df['Item'] == selected_item) & (df['Color'] == selected_color)
                if mask.any():
                    df.loc[mask, 'Stock'] += qty
                    
                    # آپدیت نهایی در گوگل شیت
                    conn.update(spreadsheet=ss_url, data=df)
                    st.success(f"موفقیت‌آمیز: {qty} عدد {selected_item} به انبار اضافه شد.")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("این کالا در جدول یافت نشد.")
        else:
            st.error("خطا: ستون‌های Item یا Color در فایل اکسل پیدا نشدند.")

except Exception as e:
    st.error(f"خطای سیستمی: {e}")
    st.info("نکته: اگر ارور 'Permission Denied' گرفتی، یعنی ایمیل سرویس اکانت را در اکسل Share نکردی.")
