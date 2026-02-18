from playwright.sync_api import sync_playwright
import time

class GSTBot:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.page = None
        self.playwright = None

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless, args=["--start-maximized"])
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = self.context.new_page()
        
    def login(self, username, password):
        if not self.page:
            self.start()
        
        try:
            print("Navigating to GST Portal...")
            self.page.goto("https://services.gst.gov.in/services/login")
            
            # Fill Credentials
            print("Filling credentials...")
            self.page.fill("#username", username)
            self.page.fill("#user_pass", password)
            self.page.fill("#captcha", "") # Focus on captcha for user
            
            # Wait for user to manually solve captcha and login
            # We can detect successful login by checking for a dashboard element
            return "Please solve the CAPTCHA and click Login on the browser window. Then enter OTP if prompted."
            
        except Exception as e:
            return f"Error during login init: {str(e)}"

    def wait_for_dashboard(self, timeout=300):
        """Waits for the user to finish login manually"""
        try:
            print("Waiting for dashboard...")
            # Dashboard URL usually contains /dashboard
            self.page.wait_for_url("**/dashboard**", timeout=timeout*1000)
            return True
        except:
            return False

    def get_notifications(self):
        """Scrapes the 'Notices and Orders' tab"""
        try:
            print("Navigating to Notices...")
            # Navigate to Services -> User Services -> View Notices and Orders
            # Note: Direct URL usually works if logged in
            self.page.goto("https://services.gst.gov.in/services/auth/viewnotices")
            self.page.wait_for_load_state("networkidle")
            
            time.sleep(2) # Extra wait for table load
            
            # Scrape basic table data
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

    def navigate_to_return_dashboard(self, financial_year, quarter, period):
        """Navigates to the file return section"""
        try:
            self.page.goto("https://services.gst.gov.in/services/auth/returns")
            self.page.wait_for_load_state("networkidle")
            
            # Select FY
            self.page.select_option("select[id='finYear']", label=financial_year)
            
            # Select Quarter (if applicable) or Period
            # Note: Selectors on GST portal change, these are approximations based on standard structure
            # Ideally this requires robust selector strategy
            
            # Assuming simplified flow: User navigates to the period manually if automation fails
            return "Navigated to Return Dashboard. Please select Period and click SEARCH."
            
        except Exception as e:
            return f"Navigation Error: {str(e)}"

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
