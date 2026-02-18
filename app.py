import streamlit as st
import pandas as pd
import database as db

st.set_page_config(page_title="AI-Accountant", page_icon="📊", layout="wide")

if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False

def check_login():
    if st.session_state['username'] == "COPL2026" and st.session_state['password'] == "COPL@2026":
        st.session_state['authentication_status'] = True
    else:
        st.session_state['authentication_status'] = False
        st.error("😕 Incorrect Username or Password")

if not st.session_state['authentication_status']:
    st.title("🔐 Login to AI-Accountant")
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password")
    st.button("Login", on_click=check_login)
    st.stop()

st.sidebar.title("Navigation")
if st.button("Logout"):
    st.session_state['authentication_status'] = False
    st.rerun()

st.title("📊 AI-Accountant for Startups")

# Fetch data
invoices = db.get_invoices()
expenses = db.get_expenses()

# Metrics
total_sales = invoices['total_amount'].sum() if not invoices.empty else 0
total_gst_collected = (invoices['igst'].sum() + invoices['cgst'].sum() + invoices['sgst'].sum()) if not invoices.empty else 0

total_expenses = expenses['total_amount'].sum() if not expenses.empty else 0
total_itc_available = (expenses['igst'].sum() + expenses['cgst'].sum() + expenses['sgst'].sum()) if not invoices.empty else 0

net_tax_payable = max(0, total_gst_collected - total_itc_available)

# Dashboard Columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Sales (Money In)", value=f"₹ {total_sales:,.2f}")
with col2:
    st.metric(label="Total Expenses (Money Out)", value=f"₹ {total_expenses:,.2f}")
with col3:
    st.metric(label="GST Collected (Liability)", value=f"₹ {total_gst_collected:,.2f}")
with col4:
    st.metric(label="Net GST Payable", value=f"₹ {net_tax_payable:,.2f}", delta_color="inverse")

st.markdown("---")

# Recent Activity
c1, c2 = st.columns(2)

with c1:
    st.subheader("Recent Invoices")
    if not invoices.empty:
        st.dataframe(invoices[['date', 'customer_name', 'total_amount', 'invoice_no']].head(5))
    else:
        st.info("No invoices added yet.")

with c2:
    st.subheader("Recent Expenses")
    if not expenses.empty:
        st.dataframe(expenses[['date', 'vendor_name', 'total_amount', 'category']].head(5))
    else:
        st.info("No expenses added yet.")

st.sidebar.success("Select a page above to manage Invoices, Expenses, or See Reports.")
st.sidebar.info("💡 **Tip:** Adding just 2-3 invoices a month takes seconds!")
