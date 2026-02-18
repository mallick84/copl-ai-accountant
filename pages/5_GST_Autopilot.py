import streamlit as st
from gst_automation import GSTBot
import database as db
import pandas as pd
import time

st.set_page_config(page_title="GST Autopilot", page_icon="✈️")

st.title("✈️ GST Autopilot Agent")
st.markdown("Automate your portal interactions. The Agent will open a browser, type for you, and fetch data.")

# Session State for Bot
if "gst_bot" not in st.session_state:
    st.session_state.gst_bot = None

with st.expander("🔐 Portal Credentials", expanded=True):
    username = st.text_input("GST Username")
    password = st.text_input("GST Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("🚀 Launch Agent & Login")
    with col2:
        stop_btn = st.button("🛑 Stop Agent")

if start_btn:
    if not username or not password:
        st.error("Please enter Username and Password")
    else:
        status_placeholder = st.empty()
        status_placeholder.info("Starting Browser...")
        
        bot = GSTBot(headless=False) # Headless=False so user can see/interact
        st.session_state.gst_bot = bot
        
        msg = bot.login(username, password)
        status_placeholder.warning(f"ACTION REQUIRED: {msg}")

if stop_btn:
    if st.session_state.gst_bot:
        st.session_state.gst_bot.close()
        st.session_state.gst_bot = None
        st.success("Agent Stopped.")

st.markdown("---")

# Feature: Notifications
st.subheader("🔔 Notifications & Notices")
if st.button("Check for Notices"):
    if not st.session_state.gst_bot:
        st.error("Please Launch Agent & Login first!")
    else:
        st.info("Checking for notices... (Make sure you are logged in on the browser)")
        
        # Check if actually logged in
        if st.session_state.gst_bot.wait_for_dashboard(timeout=5):
            notices = st.session_state.gst_bot.get_notifications()
            if notices:
                count = 0
                for n in notices:
                    # Avoid duplicates logic could go here, for now just add
                    # User will acknowledge to clear
                    db.add_notification(
                        date=n.get("Date", str(datetime.date.today())),
                        type="Portal Notice",
                        description=f"{n.get('Description')} (ID: {n.get('Notice ID')})",
                        action_required=n.get("Type", "Check Portal")
                    )
                    count += 1
                
                st.success(f"Success! {count} notices saved to Task Manager.")
                st.dataframe(pd.DataFrame(notices))
            else:
                st.success("No New Notices Found.")
        else:
            st.error("Agent could not detect Dashboard. Please complete Login in the browser window.")

# Feature: Auto-File
st.markdown("---")
st.subheader("📤 Auto-File GSTR-1")
st.warning("⚠️ This feature is in Pilot Mode. It will navigate you to the return dashboard.")

col1, col2 = st.columns(2)
with col1:
    fy = st.selectbox("Financial Year", ["2024-25", "2025-26"])
with col2:
    period = st.selectbox("Month", ["February", "March", "April"])

if st.button("Go to Return Dashboard"):
    if st.session_state.gst_bot:
        st.session_state.gst_bot.navigate_to_return_dashboard(fy, None, period)
        st.success("Navigated! Please Select Period -> Search -> Prepare Online.")
    else:
        st.error("Please Launch Agent first.")
