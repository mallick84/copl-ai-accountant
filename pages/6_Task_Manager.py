import streamlit as st
import database as db
import pandas as pd
import datetime

st.set_page_config(page_title="Task Manager", page_icon="📝")

st.title("📝 Task & Notification Manager")

tab1, tab2, tab3 = st.tabs(["⚡ My To-Do List", "🔔 Portal Notifications", "🧾 Challan Tracker"])

# --- TAB 1: TO-DO ---
with tab1:
    st.header("What to do next?")
    
    today = datetime.date.today()
    day = today.day
    
    # Logic for Compliance Dates
    tasks = []
    
    # GSTR-1 (Due 11th)
    if day <= 11:
        days_left = 11 - day
        tasks.append({
            "Task": "File GSTR-1 (Outward Supplies)",
            "Due Date": f"11th {today.strftime('%b')}",
            "Urgency": "High" if days_left < 3 else "Medium",
            "Action": "Go to GST Reports -> GSTR-1"
        })
    else:
        tasks.append({
            "Task": "File GSTR-1",
            "Due Date": f"11th {today.strftime('%b')}",
            "Urgency": "Low (Done/Passed)",
            "Action": "Check Status"
        })

    # GSTR-3B (Due 20th)
    if day <= 20:
        days_left = 20 - day
        tasks.append({
            "Task": "File GSTR-3B (Payment)",
            "Due Date": f"20th {today.strftime('%b')}",
            "Urgency": "High" if days_left < 3 else "Medium",
            "Action": "Go to GST Reports -> GSTR-3B"
        })
    else:
         tasks.append({
            "Task": "File GSTR-3B",
            "Due Date": f"20th {today.strftime('%b')}",
            "Urgency": "Low (Done/Passed)",
            "Action": "Check Status"
        })
        
    st.dataframe(pd.DataFrame(tasks))
    
    # Pending DB Notifications
    pending_notices = db.get_notifications(pending_only=True)
    if not pending_notices.empty:
        st.warning(f"You have {len(pending_notices)} pending items in 'Notifications' or 'Challan Tracker'.")

# --- TAB 2: NOTIFICATIONS ---
with tab2:
    st.header("Notices from GST Portal & Reminders")
    
    # Button to add manual reminder
    with st.expander("➕ Add Manual Reminder"):
        with st.form("manual_reminder"):
            rem_desc = st.text_input("Reminder Description")
            rem_date = st.date_input("Date", datetime.date.today())
            submitted = st.form_submit_button("Add Reminder")
            if submitted and rem_desc:
                db.add_notification(rem_date, "User Reminder", rem_desc, "Check App")
                st.success("Reminder Added!")
                st.rerun()

    # View Notifications
    notices = db.get_notifications()
    if not notices.empty:
        for index, row in notices.iterrows():
            col1, col2, col3, col4 = st.columns([2, 4, 2, 2])
            
            with col1:
                st.write(f"**{row['date']}**")
                st.caption(row['type'])
            
            with col2:
                st.write(row['description'])
                st.caption(f"Action: {row['action_required']}")
                
            with col3:
                status = row['status']
                color = "red" if status == "Pending" else "green"
                st.markdown(f":{color}[{status}]")
                
            with col4:
                if row['status'] == 'Pending':
                    if st.button("Acknowledge", key=f"ack_{row['id']}"):
                        db.update_notification_status(row['id'], "Acknowledged")
                        st.rerun()
    else:
        st.info("No notifications found.")

# --- TAB 3: CHALLAN TRACKER ---
with tab3:
    st.header("Track Payments (Challans)")
    
    with st.expander("➕ Add New Challan"):
        with st.form("challan_form"):
            cpin = st.text_input("CPIN Number")
            amount = st.number_input("Amount (₹)", min_value=1.0)
            c_date = st.date_input("Creation Date", datetime.date.today())
            
            submitted_c = st.form_submit_button("Save Challan")
            if submitted_c and cpin:
                db.add_notification(c_date, "Challan", f"CPIN: {cpin} - Amount: ₹ {amount}", "Pay at Bank/Online")
                st.success("Challan Saved!")
                st.rerun()
    
    # Filter for Challans only
    all_notifs = db.get_notifications()
    challans = all_notifs[all_notifs['type'] == 'Challan']
    
    if not challans.empty:
        for index, row in challans.iterrows():
            col1, col2, col3, col4 = st.columns([2, 4, 2, 2])
             
            with col1:
                st.write(f"**{row['date']}**")
            
            with col2:
                st.write(row['description'])
                
            with col3:
                status = row['status']
                # Remap status for UI if needed, but db stores Pending/Acknowledged
                display_status = "Unpaid" if status == "Pending" else "Paid"
                color = "red" if status == "Pending" else "green"
                st.markdown(f":{color}[{display_status}]")
                
            with col4:
                if row['status'] == 'Pending':
                    if st.button("Mark Paid", key=f"pay_{row['id']}"):
                        db.update_notification_status(row['id'], "Paid")
                        st.rerun()
    else:
        st.info("No Challans recorded.")
