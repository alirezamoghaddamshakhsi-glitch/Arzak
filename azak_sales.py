import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="AZAK Sales", page_icon="🛒")

st.title("🛒 AZAK Business Intelligence")
st.subheader("Sales & Profit Analysis")

# Connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SALES OVERVIEW ---
st.header("📊 Inventory for Sale")
data = conn.read(worksheet="Inventory")
st.table(data)

st.markdown("---")

# --- PROFIT CALCULATOR ---
st.header("💰 Smart Pricing Tool")
col1, col2 = st.columns(2)

with col1:
    cost_price = st.number_input("Manufacturing Cost (from ARZAK)", value=120000)
    sale_price = st.number_input("Selling Price (on Digikala)", value=250000)
    commission = st.slider("Marketplace Fee (%)", 0, 30, 15)

with col2:
    fee_amount = (sale_price * commission) / 100
    net_profit = sale_price - cost_price - fee_amount
    margin = (net_profit / sale_price) * 100 if sale_price > 0 else 0
    
    st.metric("Net Profit", f"{net_profit:,.0f} T")
    st.metric("Profit Margin", f"{margin:.1f}%")

st.markdown("---")

# --- SALES LOG ---
st.header("📈 Sales History")
st.write("Recent orders from marketplace will appear here.")