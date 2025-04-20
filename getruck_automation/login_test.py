from playwright.sync_api import sync_playwright, expect
import os
import sys
import datetime
import time
import re

def login_test():
    with sync_playwright() as playwright:
        # Set debug mode if parameter exists
        debug_mode = "--debug" in sys.argv
        
        # Open a new browser - ensure it's visible
        browser = playwright.chromium.launch(headless=False, slow_mo=100)
        print("Opened browser in visible mode (headless=False)", flush=True)
        
        # Create a new context
        context = browser.new_context(viewport={'width': 1200, 'height': 800})
        
        # Start tracing
        context.tracing.start(screenshots=True, snapshots=True)
        
        # Create a new page
        page = context.new_page()
        
        try:
            # Short wait before starting actions
            time.sleep(2)  # Wait for 2 seconds
            
            # Navigate to login page
            page.goto("https://platform-v51.getruck.co.il/login/")
            print("Navigated to login page", flush=True)
            
            # Additional wait to ensure page is loaded
            time.sleep(2)  # Wait for 2 seconds
            
            # If in debug mode, pause here and open Inspector
            if debug_mode:
                print("Debug mode active - Click continue in the Inspector window to proceed", flush=True)
                page.pause()
            
            # Login actions
            email_input = page.get_by_role("textbox", name="אימייל")
            email_input.wait_for(state="visible")
            email_input.click()
            email_input.fill("jafora@getruck.co")
            print("Entered email", flush=True)
            
            password_field = page.get_by_role("listitem").filter(has_text="סיסמה").locator("div").nth(2)
            password_field.wait_for(state="visible")
            password_field.click()
            
            password_input = page.get_by_role("textbox", name="סיסמה")
            password_input.wait_for(state="visible")
            password_input.fill("Jafor2024")
            print("Entered password", flush=True)
            
            time.sleep(1)  # Short wait before clicking
            
            login_button = page.locator("[data-test-id=\"Button\"]")
            login_button.wait_for(state="visible")
            login_button.click()
            print("Clicked login button", flush=True)
            
            # Wait after login
            time.sleep(3)
            
            print("Login test completed successfully", flush=True)
            
        except Exception as e:
            print(f"Error: {e}", flush=True)
            page.screenshot(path="debug/screenshots/error_screenshot.png")
            print("Error screenshot saved at debug/screenshots/error_screenshot.png", flush=True)
        finally:
            # Save tracing in any case
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            trace_path = f"debug/traces/trace_{timestamp}.zip"
            context.tracing.stop(path=trace_path)
            print(f"Trace saved in file {trace_path}", flush=True)
            browser.close()

if __name__ == "__main__":
    login_test()