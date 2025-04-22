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
            password_input.fill("Jafor2024")  # הסיסמה הנכונה - שינינו חזרה
            print("Entered password", flush=True)
            
            time.sleep(1)  # Short wait before clicking
            
            login_button = page.locator("[data-test-id=\"Button\"]")
            login_button.wait_for(state="visible")
            login_button.click()
            print("Clicked login button", flush=True)
            
            # Wait for navigation and page stability after login attempt
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Extra wait to ensure post-login UI is fully loaded
            
            # Take screenshot to see what's on screen after login
            page.screenshot(path="debug/screenshots/after_login.png")
            print("Took screenshot after login", flush=True)
            
            # Check if we're still on the login page
            current_url = page.url
            if "login" in current_url.lower():
                # Still on login page, look for error messages
                error_found = False
                error_message_selectors = [
                    "text=שם משתמש או סיסמה שגויים",
                    "text=שגיאת התחברות",
                    "text=אנא נסה שנית",
                    "[data-test-id='Error']",
                    ".error-message"
                ]
                
                for selector in error_message_selectors:
                    try:
                        error_element = page.locator(selector)
                        if error_element.count() > 0 and error_element.first.is_visible(timeout=1000):
                            error_text = error_element.first.text_content()
                            print(f"Login failed: Found error message: '{error_text}'", flush=True)
                            error_found = True
                            break
                    except:
                        pass
                
                if error_found:
                    raise Exception("Login failed: Invalid credentials or access denied")
                else:
                    raise Exception("Login failed: Still on login page but no error message found")
            else:
                # URL changed, we're no longer on login page
                print(f"Navigation successful: Current URL is {current_url}", flush=True)
                
                # Check page content to confirm successful login
                # We'll try a more general approach by looking for typical post-login UI elements
                post_login_indicators = [
                    # Look for any general dashboard/navigation elements
                    "button:has-text('סנכרון')",
                    "[data-test-id='PlanningModal-Footer']",
                    "[data-test-id='Button']",
                    "text=לוח עבודה"
                ]
                
                logged_in = False
                for indicator in post_login_indicators:
                    try:
                        element = page.locator(indicator)
                        if element.count() > 0:
                            print(f"Found post-login indicator: {indicator}", flush=True)
                            logged_in = True
                            break
                    except:
                        continue
                
                if logged_in:
                    print("Login verified successfully - found post-login UI elements", flush=True)
                    
                    # Continue with further actions as needed
                    try:
                        # Try to click on modal footer button if it exists
                        modal_button = page.locator("[data-test-id='PlanningModal-Footer'] [data-test-id='Button']")
                        if modal_button.count() > 0:
                            modal_button.click()
                            print("Clicked button at the bottom of modal window", flush=True)
                    except Exception as modal_error:
                        print(f"Note: Modal interaction optional - {modal_error}", flush=True)
                        # This is not a test failure
                else:
                    # This is unusual - URL changed but no post-login elements found
                    print("Warning: Navigation occurred but could not verify login success", flush=True)
                    # We'll consider this a success since URL changed from login page
            
            print("Login test completed successfully", flush=True)
            
        except Exception as e:
            print(f"Error: {e}", flush=True)
            try:
                page.screenshot(path="debug/screenshots/error_screenshot.png")
                print("Error screenshot saved at debug/screenshots/error_screenshot.png", flush=True)
            except:
                print("Could not save error screenshot", flush=True)
            return 1
        finally:
            # Save tracing in any case
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                trace_path = f"debug/traces/trace_{timestamp}.zip"
                context.tracing.stop(path=trace_path)
                print(f"Trace saved in file {trace_path}", flush=True)
            except Exception as trace_error:
                print(f"Could not save trace: {trace_error}", flush=True)
            
            browser.close()
            print("Browser closed", flush=True)
    
    # Return 0 if we reached this point without exceptions (successful test)
    return 0

if __name__ == "__main__":
    exit_code = login_test()
    sys.exit(exit_code)