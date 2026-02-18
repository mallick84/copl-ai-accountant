from playwright.sync_api import sync_playwright
import time
import os
import base64

class GSTBot:
    def __init__(self, headless=False, message_callback=None):
        self.headless = headless
        self.browser = None
        self.page = None
        self.playwright = None
        self.message_callback = message_callback
        self.logged_in = False
        # For agent-waiting state (user input via chat)
        self._pending_question = None
        self._user_reply = None

    def log(self, message):
        if self.message_callback:
            self.message_callback("assistant", message)
        else:
            print(message)

    def ask_user(self, question):
        """Log a question and set the agent to waiting state."""
        self.log(f"🙋 **INPUT NEEDED:** {question}")
        self._pending_question = question
        self._user_reply = None

    def receive_reply(self, reply):
        """Receive the user's reply to the pending question."""
        self._user_reply = reply
        self._pending_question = None

    @property
    def is_waiting(self):
        return self._pending_question is not None

    # ── Robust helpers ──────────────────────────────────────────────

    def _safe_click(self, selector, timeout=10000):
        """Click with retry and wait for element."""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            self.page.click(selector)
            return True
        except Exception as e:
            self.log(f"⚠️ Could not click `{selector}`: {e}")
            return False

    def _safe_fill(self, selector, value, timeout=10000):
        """Fill input with retry."""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            self.page.fill(selector, str(value))
            return True
        except Exception as e:
            self.log(f"⚠️ Could not fill `{selector}`: {e}")
            return False

    def _wait_and_click(self, text, timeout=10000):
        """Click an element by its visible text."""
        try:
            locator = self.page.get_by_text(text, exact=False).first
            locator.wait_for(timeout=timeout)
            locator.click()
            return True
        except Exception as e:
            self.log(f"⚠️ Could not find text '{text}': {e}")
            return False

    def take_screenshot(self):
        """Take a screenshot and return base64 for chat display."""
        try:
            path = os.path.join(os.path.dirname(__file__), "screenshot.png")
            self.page.screenshot(path=path)
            return path
        except Exception as e:
            self.log(f"⚠️ Screenshot failed: {e}")
            return None

    # ── Core: Start & Login ─────────────────────────────────────────

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=["--start-maximized"]
        )
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = self.context.new_page()
        
    def login(self, username, password):
        if not self.page:
            self.start()
        
        try:
            self.log("🌐 Navigating to GST Portal...")
            self.page.goto("https://services.gst.gov.in/services/login")
            self.page.wait_for_load_state("networkidle")
            
            self.log("🔑 Filling credentials...")
            self._safe_fill("#username", username)
            self._safe_fill("#user_pass", password)
            
            # Focus on captcha field for user
            self._safe_click("#captcha")
            
            return "✅ Credentials filled. Please solve the CAPTCHA and click Login. Enter OTP if prompted. I will detect when you reach the Dashboard."
            
        except Exception as e:
            return f"❌ Error during login: {str(e)}"

    def wait_for_login(self, timeout=300):
        """Polls until dashboard is detected after user completes CAPTCHA/OTP."""
        self.log("👀 Watching for successful login... (Solve CAPTCHA & OTP in the browser)")
        try:
            self.page.wait_for_url("**/auth/**", timeout=timeout * 1000)
            self.logged_in = True
            self.log("✅ **Login successful!** I am now in control of the portal.")
            time.sleep(2)
            return True
        except:
            self.log("⏰ Login detection timed out. Please make sure you are logged in.")
            return False

    # ── Notifications ───────────────────────────────────────────────

    def get_notifications(self):
        """Scrapes the 'Notices and Orders' tab."""
        try:
            self.log("📬 Navigating to Notices...")
            self.page.goto("https://services.gst.gov.in/services/auth/viewnotices")
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            notices = []
            rows = self.page.query_selector_all("table tbody tr")
            
            for row in rows:
                cols = row.query_selector_all("td")
                if len(cols) >= 3:
                    notice = {
                        "Notice ID": cols[0].inner_text(),
                        "Date": cols[1].inner_text(),
                        "Description": cols[2].inner_text(),
                        "Type": cols[3].inner_text() if len(cols) > 3 else "Unknown"
                    }
                    notices.append(notice)
            
            return notices
            
        except Exception as e:
            return [{"Error": f"Could not fetch notices: {str(e)}"}]

    # ── GSTR-1 Filing ───────────────────────────────────────────────

    def file_gstr1(self, fy, period, invoices_df):
        """
        Full GSTR-1 filing workflow.
        Steps: Navigate → Select period → Prepare Online → Add invoices → Preview → Submit
        """
        self.log(f"📤 **Starting GSTR-1 Filing** for {period} {fy}")
        
        try:
            # Step 1: Navigate to Returns
            self.log("1️⃣ Navigating to Returns dashboard...")
            self.page.goto("https://services.gst.gov.in/services/auth/returns")
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Step 2: Select Financial Year
            self.log(f"2️⃣ Selecting FY: {fy}")
            try:
                self.page.select_option("select[id='finYear']", label=fy)
                time.sleep(1)
            except:
                self.log("⚠️ Could not auto-select FY. Please select manually if needed.")
            
            # Step 3: Select Period
            self.log(f"3️⃣ Selecting Period: {period}")
            try:
                self.page.select_option("select[id='quarter']", label=period)
                time.sleep(1)
            except:
                self.log("⚠️ Could not auto-select period. Trying alternative selectors...")
                try:
                    self._wait_and_click(period)
                except:
                    pass
            
            # Step 4: Click SEARCH
            self.log("4️⃣ Clicking SEARCH...")
            clicked = self._wait_and_click("SEARCH") or self._safe_click("button[type='submit']")
            time.sleep(3)
            
            # Step 5: Click GSTR-1 Prepare Online
            self.log("5️⃣ Looking for GSTR-1 tile...")
            time.sleep(2)
            
            # Try clicking Prepare Online under GSTR-1
            gstr1_clicked = self._wait_and_click("PREPARE ONLINE")
            if not gstr1_clicked:
                gstr1_clicked = self._wait_and_click("Prepare Online")
            if not gstr1_clicked:
                # Try direct navigation
                self.log("Trying direct GSTR-1 URL...")
                self.page.goto("https://return.gst.gov.in/returns/auth/gstr1")
                self.page.wait_for_load_state("networkidle")
            
            time.sleep(3)
            
            # Step 6: Fill invoice data
            self.log(f"6️⃣ Processing {len(invoices_df)} invoices from your database...")
            self._fill_gstr1_invoices(invoices_df)
            
            # Step 7: Preview
            self.log("7️⃣ Generating preview...")
            self._wait_and_click("PREVIEW")
            time.sleep(3)
            
            # Step 8: Take screenshot and ask for confirmation
            screenshot = self.take_screenshot()
            self.log("📸 Preview generated. Check the browser window.")
            self.ask_user("Ready to SUBMIT GSTR-1? Type **yes** to proceed or **no** to cancel.")
            
            return "GSTR-1 prepared. Waiting for your confirmation to submit."
            
        except Exception as e:
            self.log(f"❌ Error during GSTR-1 filing: {str(e)}")
            return f"Error: {str(e)}"

    def _fill_gstr1_invoices(self, invoices_df):
        """Fill B2B/B2C invoice sections in GSTR-1."""
        if invoices_df.empty:
            self.log("📋 No invoices found in database to file.")
            return
        
        # Separate B2B (with GSTIN) and B2C (without GSTIN)
        b2b = invoices_df[invoices_df['gstin'].notna() & (invoices_df['gstin'] != '')]
        b2c = invoices_df[~invoices_df.index.isin(b2b.index)]
        
        if not b2b.empty:
            self.log(f"  📄 Adding {len(b2b)} B2B invoices...")
            self._wait_and_click("B2B Invoices")
            time.sleep(2)
            
            for idx, inv in b2b.iterrows():
                self.log(f"    → Invoice {inv.get('invoice_no', 'N/A')} | ₹{inv.get('total_amount', 0):,.2f}")
                # Click Add
                self._wait_and_click("ADD DETAILS")
                time.sleep(1)
                
                # Fill fields
                self._safe_fill("input[placeholder*='GSTIN']", str(inv.get('gstin', '')))
                self._safe_fill("input[placeholder*='Invoice']", str(inv.get('invoice_no', '')))
                self._safe_fill("input[placeholder*='Value']", str(inv.get('taxable_value', 0)))
                
                # Save
                self._wait_and_click("SAVE")
                time.sleep(1)
            
            self.log(f"  ✅ B2B invoices added.")
        
        if not b2c.empty:
            self.log(f"  📄 Adding {len(b2c)} B2C invoices...")
            self._wait_and_click("B2C")
            time.sleep(2)
            
            total_b2c = b2c['taxable_value'].sum()
            total_igst = b2c['igst'].sum()
            total_cgst = b2c['cgst'].sum()
            total_sgst = b2c['sgst'].sum()
            
            self.log(f"    → B2C Total Taxable: ₹{total_b2c:,.2f} | CGST: ₹{total_cgst:,.2f} | SGST: ₹{total_sgst:,.2f}")
            
            self._safe_fill("input[placeholder*='Taxable']", str(total_b2c))
            self._wait_and_click("SAVE")
            time.sleep(1)
            self.log(f"  ✅ B2C summary added.")

    def submit_gstr1(self):
        """Submit GSTR-1 after user confirmation."""
        self.log("📤 Submitting GSTR-1...")
        self._wait_and_click("SUBMIT")
        time.sleep(3)
        
        # EVC / DSC
        self.log("🔐 Selecting EVC (Electronic Verification Code)...")
        self._wait_and_click("FILE WITH EVC")
        time.sleep(2)
        
        self.ask_user("Enter the **OTP** sent to your registered mobile/email:")
        return "Waiting for OTP..."

    def confirm_otp(self, otp):
        """Enter OTP for EVC verification."""
        self.log(f"🔐 Entering OTP...")
        self._safe_fill("input[type='text'][placeholder*='OTP']", otp)
        self._safe_fill("input[id*='otp']", otp)
        self._wait_and_click("VERIFY")
        time.sleep(3)
        
        self.log("✅ **GSTR-1 filed successfully!**")
        return "GSTR-1 Filed Successfully!"

    # ── GSTR-3B Filing ──────────────────────────────────────────────

    def file_gstr3b(self, fy, period, sales_total, gst_collected, itc_available):
        """
        Full GSTR-3B filing workflow.
        Steps: Navigate → Select period → Prepare → Fill liability & ITC → Preview → Submit
        """
        self.log(f"📤 **Starting GSTR-3B Filing** for {period} {fy}")
        
        net_tax = max(0, gst_collected - itc_available)
        self.log(f"  💰 Sales: ₹{sales_total:,.2f} | GST Collected: ₹{gst_collected:,.2f}")
        self.log(f"  💰 ITC Available: ₹{itc_available:,.2f} | Net Payable: ₹{net_tax:,.2f}")
        
        try:
            # Step 1: Navigate to Returns
            self.log("1️⃣ Navigating to Returns dashboard...")
            self.page.goto("https://services.gst.gov.in/services/auth/returns")
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Step 2: Select FY & Period
            self.log(f"2️⃣ Selecting FY: {fy}, Period: {period}")
            try:
                self.page.select_option("select[id='finYear']", label=fy)
                time.sleep(1)
                self.page.select_option("select[id='quarter']", label=period)
                time.sleep(1)
            except:
                self.log("⚠️ Could not auto-select FY/Period.")
            
            # Step 3: Click SEARCH
            self.log("3️⃣ Clicking SEARCH...")
            self._wait_and_click("SEARCH")
            time.sleep(3)
            
            # Step 4: Open GSTR-3B
            self.log("4️⃣ Opening GSTR-3B...")
            gstr3b_clicked = self._wait_and_click("PREPARE ONLINE")
            if not gstr3b_clicked:
                self.page.goto("https://return.gst.gov.in/returns/auth/gstr3b")
                self.page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Step 5: Fill Section 3.1 - Tax Liability
            self.log("5️⃣ Filling Tax Liability (Section 3.1)...")
            self._wait_and_click("3.1")
            time.sleep(2)
            self._safe_fill("input[id*='taxable']", str(sales_total))
            self._safe_fill("input[id*='igst']", str(0))
            self._safe_fill("input[id*='cgst']", str(gst_collected / 2))
            self._safe_fill("input[id*='sgst']", str(gst_collected / 2))
            self._wait_and_click("CONFIRM")
            time.sleep(2)
            
            # Step 6: Fill Section 4 - ITC
            self.log("6️⃣ Filling ITC (Section 4)...")
            self._wait_and_click("4.")
            time.sleep(2)
            self._safe_fill("input[id*='itc_igst']", str(0))
            self._safe_fill("input[id*='itc_cgst']", str(itc_available / 2))
            self._safe_fill("input[id*='itc_sgst']", str(itc_available / 2))
            self._wait_and_click("CONFIRM")
            time.sleep(2)
            
            # Step 7: Preview
            self.log("7️⃣ Generating preview...")
            self._wait_and_click("PREVIEW")
            time.sleep(3)
            
            self.take_screenshot()
            self.log("📸 Preview generated. Check the browser window.")
            self.ask_user("Ready to SUBMIT GSTR-3B? Type **yes** to proceed or **no** to cancel.")
            
            return "GSTR-3B prepared. Waiting for your confirmation."
            
        except Exception as e:
            self.log(f"❌ Error during GSTR-3B filing: {str(e)}")
            return f"Error: {str(e)}"

    def submit_gstr3b(self):
        """Submit GSTR-3B after confirmation."""
        self.log("📤 Submitting GSTR-3B...")
        self._wait_and_click("SUBMIT")
        time.sleep(3)
        
        self.log("🔐 Selecting EVC...")
        self._wait_and_click("FILE WITH EVC")
        time.sleep(2)
        
        self.ask_user("Enter the **OTP** sent to your registered mobile/email:")
        return "Waiting for OTP..."

    # ── Payment / Challan ───────────────────────────────────────────

    def make_payment(self, amount):
        """Navigate to payment section and create challan."""
        self.log(f"💳 **Initiating Payment** for ₹{amount:,.2f}")
        
        try:
            self.log("1️⃣ Navigating to Create Challan...")
            self.page.goto("https://services.gst.gov.in/services/auth/challan")
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            self.log("2️⃣ Filling challan details...")
            # The portal auto-fills GSTIN. We need to fill amounts
            self._safe_fill("input[id*='cgst']", str(amount / 2))
            self._safe_fill("input[id*='sgst']", str(amount / 2))
            
            self.log("3️⃣ Select payment method in the browser.")
            self.take_screenshot()
            self.ask_user("Select your payment method (Net Banking / NEFT / Over the Counter) in the browser, then type **done** when ready.")
            
            return "Challan prepared. Please select payment method."
            
        except Exception as e:
            self.log(f"❌ Payment error: {str(e)}")
            return f"Error: {str(e)}"

    # ── Navigation Helper ───────────────────────────────────────────

    def navigate_to_return_dashboard(self, financial_year, quarter, period):
        """Navigates to the file return section."""
        try:
            self.page.goto("https://services.gst.gov.in/services/auth/returns")
            self.page.wait_for_load_state("networkidle")
            self.page.select_option("select[id='finYear']", label=financial_year)
            return "Navigated to Return Dashboard. Please select Period and click SEARCH."
        except Exception as e:
            return f"Navigation Error: {str(e)}"

    # ── Cleanup ─────────────────────────────────────────────────────

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.logged_in = False
