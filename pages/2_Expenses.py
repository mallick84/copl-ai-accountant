import streamlit as st
import database as db
import datetime

st.set_page_config(page_title="Expenses", page_icon="💸")

st.title("💸 Expenses & Purchases")

with st.expander("➕ Add New Expense", expanded=True):
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Expense Date", datetime.date.today())
            vendor_name = st.text_input("Vendor Name")
            gstin = st.text_input("Vendor GSTIN (Optional)")
            category = st.selectbox("Category", ["Office Supplies", "Raw Material", "Services", "Utilities", "Other"])
        
        with col2:
            description = st.text_input("Description")
            taxable_value = st.number_input("Taxable Value (₹)", min_value=0.0, format="%.2f")
            gst_rate = st.selectbox("GST Rate (%)", [0, 5, 12, 18, 28], index=3)
            place_of_supply = st.radio("Place of Supply", ["Intra-State (Within State)", "Inter-State (Outside State)"])
        
        # Auto-calculate taxes
        igst = 0.0
        cgst = 0.0
        sgst = 0.0
        
        total_gst = taxable_value * (gst_rate / 100)
        
        if place_of_supply == "Inter-State (Outside State)":
            igst = total_gst
        else:
            cgst = total_gst / 2
            sgst = total_gst / 2
            
        total_amount = taxable_value + total_gst
        
        st.markdown(f"**Calculated Tax:** IGST: {igst:.2f} | CGST: {cgst:.2f} | SGST: {sgst:.2f}")
        st.markdown(f"### Total Expense Amount: ₹ {total_amount:,.2f}")
        
        submitted = st.form_submit_button("Save Expense")
        if submitted:
            if not vendor_name:
                st.error("Vendor Name is required.")
            else:
                db.add_expense(date, vendor_name, gstin, category, taxable_value, gst_rate, igst, cgst, sgst, total_amount, description)
                st.success("Expense Saved Successfully!")
                st.rerun()

st.markdown("---")
st.subheader("📉 Expense History")
df = db.get_expenses()
if not df.empty:
    st.dataframe(df)
else:
    st.info("No expenses found.")
