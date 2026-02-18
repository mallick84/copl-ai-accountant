import streamlit as st
import database as db
import pandas as pd

st.set_page_config(page_title="GST Reports", page_icon="📑")

st.title("📑 GST Reports & Filing Helper")

invoices = db.get_invoices()
expenses = db.get_expenses()

tab1, tab2 = st.tabs(["GSTR-1 (Sales)", "GSTR-3B (Summary)"])

with tab1:
    st.header("GSTR-1 (Outward Supplies)")
    st.info("Use these details to file GSTR-1 on the GST Portal.")
    
    if not invoices.empty:
        # Group by Rate
        summary = invoices.groupby('gst_rate')[['taxable_value', 'igst', 'cgst', 'sgst', 'total_amount']].sum().reset_index()
        st.dataframe(summary)
        
        st.download_button(
            label="Download GSTR-1 Data (CSV)",
            data=invoices.to_csv(index=False),
            file_name='gstr1_sales_data.csv',
            mime='text/csv',
        )
    else:
        st.warning("No sales data available.")

with tab2:
    st.header("GSTR-3B (Monthly Return)")
    st.info("This is your Input Tax Credit (ITC) vs Liability Check.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Liability (Tax on Sales)")
        if not invoices.empty:
            total_liab_igst = invoices['igst'].sum()
            total_liab_cgst = invoices['cgst'].sum()
            total_liab_sgst = invoices['sgst'].sum()
            
            st.write(f"**IGST:** ₹ {total_liab_igst:,.2f}")
            st.write(f"**CGST:** ₹ {total_liab_cgst:,.2f}")
            st.write(f"**SGST:** ₹ {total_liab_sgst:,.2f}")
            st.markdown(f"**Total Liability:** ₹ {(total_liab_igst + total_liab_cgst + total_liab_sgst):,.2f}")
        else:
            st.write("No sales recorded.")

    with col2:
        st.subheader("Input Tax Credit (Tax on Purchases)")
        if not expenses.empty:
            total_itc_igst = expenses['igst'].sum()
            total_itc_cgst = expenses['cgst'].sum()
            total_itc_sgst = expenses['sgst'].sum()
            
            st.write(f"**IGST:** ₹ {total_itc_igst:,.2f}")
            st.write(f"**CGST:** ₹ {total_itc_cgst:,.2f}")
            st.write(f"**SGST:** ₹ {total_itc_sgst:,.2f}")
            st.markdown(f"**Total ITC Available:** ₹ {(total_itc_igst + total_itc_cgst + total_itc_sgst):,.2f}")
        else:
            st.write("No expenses recorded.")
    
    st.markdown("---")
    
    # Net Payable Calculation
    net_igst = max(0, (invoices['igst'].sum() if not invoices.empty else 0) - (expenses['igst'].sum() if not expenses.empty else 0))
    net_cgst = max(0, (invoices['cgst'].sum() if not invoices.empty else 0) - (expenses['cgst'].sum() if not expenses.empty else 0))
    net_sgst = max(0, (invoices['sgst'].sum() if not invoices.empty else 0) - (expenses['sgst'].sum() if not expenses.empty else 0))
    
    st.subheader(f"💵 Net Tax Payable in Cash: ₹ {(net_igst + net_cgst + net_sgst):,.2f}")
    st.caption("Simplified calculation. Verify with portal before payment.")
