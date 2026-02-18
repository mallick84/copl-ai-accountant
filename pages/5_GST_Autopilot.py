import streamlit as st
from gst_automation import GSTBot
import database as db
import pandas as pd
import time
import datetime

st.set_page_config(page_title="GST Autopilot", page_icon="✈️")

st.title("✈️ GST Autopilot Agent")
st.markdown("The AI Agent automates your GST filing. It will take control of the browser after login.")

# ── Session State ────────────────────────────────────────────────

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "gst_bot" not in st.session_state:
    st.session_state.gst_bot = None
if "agent_state" not in st.session_state:
    st.session_state.agent_state = "idle"  # idle, logging_in, active, waiting_confirm, waiting_otp

def bot_log(role, message):
    st.session_state.chat_history.append({"role": role, "content": message})

# ── Sidebar Controls ─────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Agent Controls")
    
    # Status indicator
    state = st.session_state.agent_state
    if state == "idle":
        st.info("🔴 Agent: Offline")
    elif state == "logging_in":
        st.warning("🟡 Agent: Waiting for Login")
    elif state == "active":
        st.success("🟢 Agent: Active & Ready")
    elif state in ("waiting_confirm", "waiting_otp"):
        st.warning("🟠 Agent: Waiting for Your Input")
    
    st.markdown("---")
    
    # Login Section
    username = st.text_input("GST Username", key="gst_username")
    password = st.text_input("GST Password", type="password", key="gst_password")
    
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("🚀 Launch", use_container_width=True)
    with col2:
        stop_btn = st.button("🛑 Stop", use_container_width=True)
    
    if state == "logging_in":
        if st.button("✅ I've Logged In", use_container_width=True):
            bot = st.session_state.gst_bot
            if bot:
                bot_log("user", "I've completed login (CAPTCHA + OTP)")
                success = bot.wait_for_login(timeout=10)
                if success:
                    st.session_state.agent_state = "active"
                else:
                    # Even if URL detection fails, trust the user
                    bot.logged_in = True
                    st.session_state.agent_state = "active"
                    bot_log("assistant", "✅ Understood! I'm now in control. Use the actions below to start filing.")
                st.rerun()
    
    # Filing Actions (only when active)
    if state in ("active", "waiting_confirm", "waiting_otp"):
        st.markdown("---")
        st.subheader("📋 Filing Actions")
        
        fy = st.selectbox("Financial Year", ["2024-25", "2025-26"])
        period = st.selectbox("Period", ["January", "February", "March", "April", "May", "June", 
                                          "July", "August", "September", "October", "November", "December"])
        
        if st.button("📤 File GSTR-1", use_container_width=True):
            bot = st.session_state.gst_bot
            if bot:
                bot_log("user", f"File GSTR-1 for {period} {fy}")
                invoices = db.get_invoices()
                bot.file_gstr1(fy, period, invoices)
                st.session_state.agent_state = "waiting_confirm"
                st.rerun()
        
        if st.button("📤 File GSTR-3B", use_container_width=True):
            bot = st.session_state.gst_bot
            if bot:
                bot_log("user", f"File GSTR-3B for {period} {fy}")
                invoices = db.get_invoices()
                expenses = db.get_expenses()
                
                sales_total = invoices['taxable_value'].sum() if not invoices.empty else 0
                gst_collected = (invoices['igst'].sum() + invoices['cgst'].sum() + invoices['sgst'].sum()) if not invoices.empty else 0
                itc_available = (expenses['igst'].sum() + expenses['cgst'].sum() + expenses['sgst'].sum()) if not expenses.empty else 0
                
                bot.file_gstr3b(fy, period, sales_total, gst_collected, itc_available)
                st.session_state.agent_state = "waiting_confirm"
                st.rerun()
        
        net_payable = 0
        invoices = db.get_invoices()
        expenses = db.get_expenses()
        gst_collected = (invoices['igst'].sum() + invoices['cgst'].sum() + invoices['sgst'].sum()) if not invoices.empty else 0
        itc_available = (expenses['igst'].sum() + expenses['cgst'].sum() + expenses['sgst'].sum()) if not expenses.empty else 0
        net_payable = max(0, gst_collected - itc_available)
        
        if net_payable > 0:
            st.metric("Net Tax Payable", f"₹{net_payable:,.2f}")
            if st.button("💳 Make Payment", use_container_width=True):
                bot = st.session_state.gst_bot
                if bot:
                    bot_log("user", f"Make payment of ₹{net_payable:,.2f}")
                    bot.make_payment(net_payable)
                    st.session_state.agent_state = "waiting_confirm"
                    st.rerun()
        
        st.markdown("---")
        if st.button("🔔 Check Notices", use_container_width=True):
            bot = st.session_state.gst_bot
            if bot:
                bot_log("user", "Check for notices")
                notices = bot.get_notifications()
                if notices and "Error" not in notices[0]:
                    bot_log("assistant", f"Found {len(notices)} notices.")
                    for n in notices:
                        db.add_notification(
                            date=n.get("Date", str(datetime.date.today())),
                            type="Portal Notice",
                            description=f"{n.get('Description')} (ID: {n.get('Notice ID')})",
                            action_required=n.get("Type", "Check Portal")
                        )
                    bot_log("assistant", f"Saved {len(notices)} notices to Task Manager.")
                else:
                    bot_log("assistant", "No notices found.")
                st.rerun()

# ── Main Chat Interface ─────────────────────────────────────────

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Handle Start / Stop ─────────────────────────────────────────

if start_btn:
    if not username or not password:
        st.error("Please enter credentials in the sidebar.")
    else:
        bot_log("user", "Launch Agent")
        bot = GSTBot(headless=False, message_callback=bot_log)
        st.session_state.gst_bot = bot
        msg = bot.login(username, password)
        bot_log("assistant", msg)
        st.session_state.agent_state = "logging_in"
        st.rerun()

if stop_btn:
    if st.session_state.gst_bot:
        bot_log("user", "Stop Agent")
        st.session_state.gst_bot.close()
        st.session_state.gst_bot = None
        bot_log("assistant", "🛑 Agent stopped.")
        st.session_state.agent_state = "idle"
        st.rerun()

# ── User Chat Input ──────────────────────────────────────────────

if prompt := st.chat_input("Type a message or reply to the Agent..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    bot = st.session_state.gst_bot
    
    if not bot:
        bot_log("assistant", "Please launch the agent first from the sidebar.")
        st.rerun()
    
    # Handle agent-waiting states
    elif st.session_state.agent_state == "waiting_confirm":
        if prompt.lower() in ("yes", "y", "confirm", "proceed"):
            bot_log("assistant", "✅ Confirmed! Proceeding with submission...")
            bot.receive_reply("yes")
            # Determine which form to submit
            last_msgs = [m["content"] for m in st.session_state.chat_history if m["role"] == "assistant"]
            if any("GSTR-1" in m for m in last_msgs[-5:]):
                bot.submit_gstr1()
                st.session_state.agent_state = "waiting_otp"
            elif any("GSTR-3B" in m for m in last_msgs[-5:]):
                bot.submit_gstr3b()
                st.session_state.agent_state = "waiting_otp"
            else:
                bot_log("assistant", "Proceeding...")
                st.session_state.agent_state = "active"
        elif prompt.lower() in ("no", "n", "cancel"):
            bot_log("assistant", "❌ Cancelled. No submission was made.")
            bot.receive_reply("no")
            st.session_state.agent_state = "active"
        else:
            bot_log("assistant", "Please type **yes** to confirm or **no** to cancel.")
        st.rerun()
    
    elif st.session_state.agent_state == "waiting_otp":
        bot_log("assistant", f"🔐 Entering OTP...")
        result = bot.confirm_otp(prompt.strip())
        bot_log("assistant", result)
        st.session_state.agent_state = "active"
        st.rerun()
    
    else:
        # General chat
        bot_log("assistant", "👍 Noted. Use the sidebar actions to tell me what to do, or I'll respond to specific commands.")
        st.rerun()
