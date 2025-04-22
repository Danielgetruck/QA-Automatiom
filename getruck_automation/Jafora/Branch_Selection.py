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
            page.wait_for_load_state("networkidle")
            
            # If in debug mode, pause here and open Inspector
            if debug_mode:
                print("Debug mode active - Click continue in the Inspector window to proceed", flush=True)
                page.pause()
            
            # Login actions - with better error handling
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
            
            # Click login button with proper waiting
            login_button = page.locator("[data-test-id=\"Button\"]")
            login_button.wait_for(state="visible")
            login_button.click()
            print("Clicked login button", flush=True)
            
            # Wait for navigation after login
            page.wait_for_load_state("networkidle")
            
            # Click on modal footer button with waiting
            modal_button = page.locator("[data-test-id=\"PlanningModal-Footer\"] [data-test-id=\"Button\"]")
            modal_button.wait_for(state="visible", timeout=10000)
            modal_button.click()
            print("Clicked button at the bottom of modal window", flush=True)
            
            # Wait for form to be ready
            time.sleep(2)
            
            # Enter plan name
            plan_input = page.locator("[data-test-id=\"CreatePlan-Modal-Ul-Input\"]")
            plan_input.wait_for(state="visible")
            plan_input.click()
            plan_input.fill("דניאל בדיקות")
            print("Entered name: Daniel Tests", flush=True)
            
            # Select date
            date_picker = page.locator("[data-test-id=\"CreatePlanModal-Ul-DatePicker-picker\"]")
            date_picker.wait_for(state="visible")
            date_picker.click()
            
            date_cell = page.get_by_role("cell", name="21").first
            date_cell.wait_for(state="visible")
            date_cell.dblclick()
            print("Selected date 21", flush=True)
            
            # Select branch
            branch_dropdown = page.locator("#modal [data-test-id=\"Drop-Down\"]").get_by_role("list").get_by_text("סניף")
            branch_dropdown.wait_for(state="visible")
            branch_dropdown.click()
            print("Clicked branch selection", flush=True)
            
            # Wait for dropdown to open fully
            time.sleep(1)
            
            # Select branch 70
            branch_option = page.get_by_text("סניף 70")
            branch_option.wait_for(state="visible")
            branch_option.click()
            print("Selected branch 70", flush=True)
            
            # Create button click
            create_button = page.locator("[data-test-id=\"CreatePlanModal-NewButton\"]")
            create_button.wait_for(state="visible")
            create_button.click()
            print("Clicked create button", flush=True)
            
            print("Test completed successfully", flush=True)
            
        except Exception as e:
            print(f"Error: {e}", flush=True)
            try:
                page.screenshot(path="debug/screenshots/error_screenshot.png")
                print("Error screenshot saved at debug/screenshots/error_screenshot.png", flush=True)
            except:
                print("Failed to save error screenshot", flush=True)
        
        finally:
            # Save tracing in any case
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                trace_path = f"debug/traces/trace_{timestamp}.zip"
                context.tracing.stop(path=trace_path)
                print(f"Trace saved in file {trace_path}", flush=True)
            except Exception as e:
                print(f"Failed to save trace: {e}", flush=True)
                
            # Close browser
            browser.close()
            print("Browser closed", flush=True)

if __name__ == "__main__":
    login_test()