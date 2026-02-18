import streamlit as st
import database as db
import pandas as pd

st.set_page_config(page_title="AI Accountant", page_icon="🤖")

st.title("🤖 AI Accountant")
st.write("Ask me about your business finances!")

query = st.text_input("Ask a question (e.g., 'Total sales', 'How much tax do I owe?', 'List expenses')")

if query:
    query = query.lower()
    invoices = db.get_invoices()
    expenses = db.get_expenses()
    
    response = ""
    
    if "total sales" in query or "revenue" in query or "income" in query:
        total = invoices['total_amount'].sum() if not invoices.empty else 0
        response = f"Your total sales revenue is **₹ {total:,.2f}**."
        
    elif "tax" in query or "gst" in query or "owe" in query:
        total_liability = (invoices['igst'].sum() + invoices['cgst'].sum() + invoices['sgst'].sum()) if not invoices.empty else 0
        total_itc = (expenses['igst'].sum() + expenses['cgst'].sum() + expenses['sgst'].sum()) if not invoices.empty else 0
        net = max(0, total_liability - total_itc)
        response = (f"**GST Liability:** ₹ {total_liability:,.2f}\n\n"
                    f"**ITC Available:** ₹ {total_itc:,.2f}\n\n"
                    f"**Net Payable:** ₹ {net:,.2f}")
        
    elif "expense" in query or "spending" in query or "cost" in query:
        total_exp = expenses['total_amount'].sum() if not expenses.empty else 0
        response = f"Your total expenses are **₹ {total_exp:,.2f}**."
        if not expenses.empty:
            top_category = expenses.groupby('category')['total_amount'].sum().idxmax()
            response += f"\n\nYour highest spending category is **{top_category}**."
            
    elif "profit" in query:
        sales = invoices['taxable_value'].sum() if not invoices.empty else 0
        costs = expenses['taxable_value'].sum() if not expenses.empty else 0
        profit = sales - costs
        response = f"Your estimated gross profit (Taxable Sales - Taxable Expenses) is **₹ {profit:,.2f}**."
        
    else:
        response = "I'm a simple AI. I can answer questions about: 'Total Sales', 'Expenses', 'Tax Payable', 'Profit'."
    
    st.markdown("### Answer:")
    st.info(response)
