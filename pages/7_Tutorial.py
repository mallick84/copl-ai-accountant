import streamlit as st

st.set_page_config(page_title="Tutorial", page_icon="📚", layout="wide")

st.title("📚 AI-Accountant Tutorial")
st.markdown("### User Guide & Operational Procedure")

st.markdown("""
Welcome to **AI-Accountant**, your AI-powered financial assistant. This application is designed to help you manage your business finances, automate GST compliance, and track your tasks efficiently.

Here is a step-by-step guide on how to use each feature of the application.
""")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💰 Sales & Invoices", 
    "💸 Expenses", 
    "📊 GST Reports", 
    "🤖 AI Assistant", 
    "🚀 GST Autopilot", 
    "✅ Task Manager"
])

with tab1:
    st.header("💰 Sales & Invoices")
    st.markdown("""
    **Navigate to:** `1_Sales_Invoices` in the sidebar.

    1.  **Create New Invoice**:
        -   Enter the **Customer Name**, **Invoice Number**, and **Date**.
        -   Add items by specifying the **Description**, **HSN Code**, **Quantity**, **Rate**, and **GST Rate (%)**.
        -   The system automatically calculates the **Taxable Value**, **CGST**, **SGST/IGST**, and **Total Amount**.
        -   Click **Save Invoice** to record the transaction in the database.
    
    2.  **View Invoices**:
        -   Scroll down to see a list of all recorded sales invoices.
        -   You can filter or search for specific invoices (functionality may vary based on current updates).
    """)

with tab2:
    st.header("💸 Expenses")
    st.markdown("""
    **Navigate to:** `2_Expenses` in the sidebar.

    1.  **Record Expense**:
        -   Enter the **Vendor Name**, **Invoice/Bill Number**, and **Date**.
        -   Select the **Expense Category** (e.g., Rent, Utilities, Purchase of Goods).
        -   Enter the **Taxable Value** and applicable **GST Rate**.
        -   Click **Save Expense**.
    
    2.  **Expense Tracking**:
        -   View a history of all expenses to keep track of your outflow.
        -   This data is crucial for calculating your Input Tax Credit (ITC).
    """)

with tab3:
    st.header("📊 GST Reports")
    st.markdown("""
    **Navigate to:** `3_GST_Reports` in the sidebar.

    1.  **GSTR-1 (Sales)**:
        -   Generates a summary of all outward supplies (sales).
        -   Use this for filing your GSTR-1 return.
    
    2.  **GSTR-3B (Summary)**:
        -   Provides a summary of your sales and eligible Input Tax Credit (ITC).
        -   Calculates the net tax liability you need to pay.
    
    3.  **Profit & Loss**:
        -   Analyses your total Sales vs. Total Expenses to show your Net Profit or Loss for the period.
    """)

with tab4:
    st.header("🤖 AI Assistant")
    st.markdown("""
    **Navigate to:** `4_AI_Assistant` in the sidebar.

    1.  **Ask Questions**:
        -   Use the chat interface to ask questions about your financial data.
        -   *Examples:*
            -   "What was my total sales last month?"
            -   "Who is my top customer?"
            -   "How much tax do I owe?"
    
    2.  **Insights**:
        -   The AI analyzes your database to provide instant answers and insights, saving you from manual calculations.
    """)

with tab5:
    st.header("🚀 GST Autopilot")
    st.markdown("""
    **Navigate to:** `5_GST_Autopilot` in the sidebar.

    1.  **Automation Dashboard**:
        -   View the status of automated tasks like simple return filings (Nil returns) or payment verifications.
    
    2.  **Notifications**:
        -   The system checks for new GST notifications and alerts you to important deadlines or changes.
    
    3.  **Challan Tracking**:
        -   Monitor the status of your tax payment challans.
    """)

with tab6:
    st.header("✅ Task Manager")
    st.markdown("""
    **Navigate to:** `6_Task_Manager` in the sidebar.

    1.  **Compliance Calendar**:
        -   Automatically generated tasks based on GST due dates (e.g., "File GSTR-1 by 11th").
    
    2.  **Manage Tasks**:
        -   Mark tasks as **Completed** once you have finished them.
        -   Add manual tasks if you have other compliance requirements.
    """)

st.markdown("---")
st.info("💡 **Tip:** Keep your data updated regularly to get the most accurate reports and AI insights.")
