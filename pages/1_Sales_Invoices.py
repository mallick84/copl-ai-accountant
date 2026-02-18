import streamlit as st
import database as db
import datetime

st.set_page_config(page_title="Sales Invoices", page_icon="💰")

st.title("💰 Sales & Invoices")

with st.expander("➕ Add New Invoice", expanded=True):
    with st.form("invoice_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Invoice Date", datetime.date.today())
            invoice_no = st.text_input("Invoice Number")
            customer_name = st.text_input("Customer Name")
            gstin = st.text_input("Customer GSTIN (Optional)")
        
        with col2:
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
        st.markdown(f"### Total Invoice Amount: ₹ {total_amount:,.2f}")
        
        submitted = st.form_submit_button("Save Invoice")
        if submitted:
            if not invoice_no or not customer_name:
                st.error("Invoice Number and Customer Name are required.")
            else:
                db.add_invoice(date, invoice_no, customer_name, gstin, taxable_value, gst_rate, igst, cgst, sgst, total_amount)
                st.success("Invoice Saved Successfully!")
                st.rerun()

st.markdown("---")
st.subheader("📋 Invoice History")
df = db.get_invoices()
if not df.empty:
    st.dataframe(df)
else:
    st.info("No invoices found.")
