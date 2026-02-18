import streamlit as st
from gst_automation import GSTBot
import database as db
import pandas as pd
import time

st.set_page_config(page_title="GST Autopilot", page_icon="✈️")

st.title("✈️ GST Autopilot Agent")
st.markdown("Automate your portal interactions. The Agent will open a browser, type for you, and fetch data.")


# Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def bot_log(role, message):
    st.session_state.chat_history.append({"role": role, "content": message})

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Agent Controls")
    username = st.text_input("GST Username", key="gst_username")
    password = st.text_input("GST Password", type="password", key="gst_password")
    
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("🚀 Launch Agent")
    with col2:
        stop_btn = st.button("🛑 Stop Agent")

    st.markdown("---")
    st.subheader("Automations")
    if st.button("Check Notices"):
        if st.session_state.gst_bot:
            bot_log("user", "Check for notices")
            notices = st.session_state.gst_bot.get_notifications()
            if notices:
                bot_log("assistant", f"Found {len(notices)} notices.")
                db_count = 0 
                for n in notices:
                    db.add_notification(
                        date=n.get("Date", str(datetime.date.today())),
                        type="Portal Notice",
                        description=f"{n.get('Description')} (ID: {n.get('Notice ID')})",
                        action_required=n.get("Type", "Check Portal")
                    )
                    db_count += 1
                bot_log("assistant", f"Saved {db_count} notices to Task Manager.")
            else:
                bot_log("assistant", "No notices found.")
        else:
            st.error("Agent not running")

    st.markdown("---")
    st.write("📤 **Auto-File GSTR-1**")
    fy = st.selectbox("FY", ["2024-25", "2025-26"])
    period = st.selectbox("Month", ["February", "March", "April"])
    if st.button("Go to Return Dashboard"):
        if st.session_state.gst_bot:
            bot_log("user", f"Navigate to Returns: {period} {fy}")
            msg = st.session_state.gst_bot.navigate_to_return_dashboard(fy, None, period)
            bot_log("assistant", msg)
        else:
            st.error("Agent not running")

# Main Chat Interface
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle Start/Stop
if start_btn:
    if not username or not password:
        st.error("Please enter credentials in the sidebar.")
    else:
        bot_log("user", "Launch Agent")
        bot = GSTBot(headless=False, message_callback=bot_log)
        st.session_state.gst_bot = bot
        msg = bot.login(username, password)
        bot_log("assistant", msg)
        st.rerun()

if stop_btn:
    if st.session_state.gst_bot:
        bot_log("user", "Stop Agent")
        st.session_state.gst_bot.close()
        st.session_state.gst_bot = None
        bot_log("assistant", "Agent stopped.")
        st.rerun()

# User Input (Chat)
if prompt := st.chat_input("Type a message or instruction for the Agent..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Simple response logic for now
    if st.session_state.gst_bot:
        with st.chat_message("assistant"):
            response = "I heard you. Currently, I only respond to sidebar commands, but I'm listening!"
            st.write(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
    else:
        with st.chat_message("assistant"):
            st.write("Please launch the agent first from the sidebar.")

