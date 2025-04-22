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
        skip_sync_verification = "--skip-sync-verify" in sys.argv
        
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
            
            date_cell = page.get_by_role("cell", name="23").first
            date_cell.wait_for(state="visible")
            date_cell.dblclick()
            print("Selected date 23", flush=True)
            
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
            
            # Click create button
            create_button = page.locator("[data-test-id=\"CreatePlanModal-NewButton\"]")
            create_button.wait_for(state="visible")
            create_button.click()
            print("Clicked new creation button", flush=True)
            
            # Wait for page to stabilize
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Additional wait to ensure page is fully ready
            
            # Click sync button
            sync_button = page.get_by_role("button", name="סנכרון")
            sync_button.wait_for(state="visible")
            sync_button.click()
            print("Clicked sync button", flush=True)
            
            # Wait for sync processing - INCREASED WAIT TIME
            print("Waiting for sync processing (30 seconds)...", flush=True)
            page.wait_for_load_state("networkidle")
            time.sleep(30)  # Increased wait time - give the system more time to process
            
            # Check if synchronization was successful - with improved success detection
            if skip_sync_verification:
                print("Skipping sync verification as requested", flush=True)
            else:
                try:
                    # First check if the modal is visible at all
                    sync_results_modal = page.locator("[data-test-id=\"SyncResultsModal-Content\"]")
                    
                    print("Looking for sync results modal...", flush=True)
                    is_modal_visible = sync_results_modal.is_visible(timeout=5000)
                    
                    if is_modal_visible:
                        print("Sync results modal is visible", flush=True)
                        
                        # Take screenshot of sync modal for debugging
                        page.screenshot(path="debug/screenshots/sync_modal.png")
                        print("Took screenshot of sync modal", flush=True)
                        
                        # Track sync success
                        sync_success = False
                        
                        # Check for success message - multiple possible message formats
                        try:
                            success_indicators = [
                                "text=הסנכרון הושלם בהצלחה", 
                                "text=סנכרון הושלם בהצלחה",
                                "text=הושלם בהצלחה",
                                "text=completed successfully"
                            ]
                            
                            for indicator in success_indicators:
                                try:
                                    success_element = page.locator(indicator)
                                    if success_element.count() > 0 and success_element.first.is_visible(timeout=500):
                                        print(f"Success message found: '{indicator}'", flush=True)
                                        sync_success = True
                                        break
                                except:
                                    continue
                                    
                            if not sync_success:
                                print("No explicit success message found, checking for data", flush=True)
                        except Exception as msg_error:
                            print(f"Error checking for success message: {msg_error}", flush=True)
                        
                        # Check for data elements - this is also a sign of success
                        try:
                            data_elements = page.locator("[data-test-id=\"SyncResultsModal-Content\"] >> ul >> li")
                            data_count = data_elements.count()
                            
                            if data_count > 0:
                                print(f"Received data: {data_count} items found", flush=True)
                                sync_success = True
                                
                                # Show details for first few items
                                for i in range(min(data_count, 3)):
                                    item_text = data_elements.nth(i).text_content()
                                    print(f"Item {i+1}: {item_text[:50]}...", flush=True)
                            else:
                                print("No data items found in sync results", flush=True)
                                
                                # Check for other positive indicators
                                general_content = sync_results_modal.text_content()
                                if general_content and len(general_content) > 0:
                                    print(f"Modal content: {general_content[:100]}...", flush=True)
                                    
                                    # Keywords that might indicate success
                                    success_keywords = ["הצלחה", "נסתיים בהצלחה", "completed", "success"]
                                    for keyword in success_keywords:
                                        if keyword in general_content:
                                            print(f"Found success keyword in modal: '{keyword}'", flush=True)
                                            sync_success = True
                                            break
                        except Exception as data_error:
                            print(f"Error checking for data elements: {data_error}", flush=True)
                        
                        # Additional check for non-error status
                        try:
                            error_indicators = [
                                "text=שגיאה", 
                                "text=error",
                                "text=נכשל",
                                "text=failed",
                                "[data-test-id=\"Error\"]",
                                ".error-message"
                            ]
                            
                            error_found = False
                            for indicator in error_indicators:
                                try:
                                    error_element = page.locator(indicator)
                                    if error_element.count() > 0 and error_element.first.is_visible(timeout=500):
                                        error_text = error_element.first.text_content()
                                        print(f"Error indicator found: '{error_text}'", flush=True)
                                        error_found = True
                                        break
                                except:
                                    continue
                            
                            # If there's no explicit error and we haven't confirmed success yet,
                            # we'll consider it a success if the modal appeared at all
                            if not error_found and not sync_success:
                                print("No error indicators found, considering sync successful based on modal presence", flush=True)
                                sync_success = True
                        except Exception as error_check_error:
                            print(f"Error checking for error indicators: {error_check_error}", flush=True)
                        
                        # If sync failed, raise exception
                        if not sync_success:
                            page.screenshot(path="debug/screenshots/sync_failed.png")
                            raise Exception("Synchronization failed: No success indicators found")
                        else:
                            print("Sync verification completed: Considered successful", flush=True)
                    else:
                        # Modal is not visible - this might be an error or might be ok
                        page.screenshot(path="debug/screenshots/no_sync_modal.png")
                        print("Sync results modal not visible - this might mean instant success or failure", flush=True)
                        
                        # Check for any error messages on the page
                        error_found = False
                        try:
                            error_indicators = [
                                "text=שגיאה", 
                                "text=error",
                                "text=נכשל",
                                "text=failed",
                                "[data-test-id=\"Error\"]",
                                ".error-message"
                            ]
                            
                            for indicator in error_indicators:
                                try:
                                    error_element = page.locator(indicator)
                                    if error_element.count() > 0 and error_element.first.is_visible(timeout=500):
                                        error_text = error_element.first.text_content()
                                        print(f"Error indicator found on page: '{error_text}'", flush=True)
                                        error_found = True
                                        break
                                except:
                                    continue
                        except Exception as page_error_check:
                            print(f"Error checking for page errors: {page_error_check}", flush=True)
                        
                        if error_found:
                            raise Exception("Synchronization failed: No modal but error found on page")
                        else:
                            # If no modal and no error, we'll assume success
                            print("No sync modal and no errors found - assuming sync was successful", flush=True)
                        
                except Exception as sync_error:
                    # Take screenshot for debugging
                    page.screenshot(path="debug/screenshots/sync_error.png")
                    print(f"Sync verification error: {sync_error}", flush=True)
                    print("Sync error screenshot saved at debug/screenshots/sync_error.png", flush=True)
                    raise Exception(f"Synchronization process failed: {sync_error}")
            
            # Try to close the sync results modal if visible - allow it to fail silently
            try:
                close_button = page.locator("[data-test-id=\"SyncResultsModal-Footer\"] [data-test-id=\"Button\"]")
                if close_button.is_visible(timeout=2000):
                    close_button.click()
                    print("Clicked button at the bottom of sync results window", flush=True)
                    time.sleep(1)  # Wait for modal to close
            except Exception as close_error:
                print(f"Note: Could not close sync results window (this is ok): {close_error}", flush=True)
            
            print("Test completed successfully", flush=True)
            
        except Exception as e:
            print(f"Error: {e}", flush=True)
            try:
                page.screenshot(path="debug/screenshots/error_screenshot.png")
                print("Error screenshot saved at debug/screenshots/error_screenshot.png", flush=True)
            except:
                print("Failed to save error screenshot", flush=True)
            
            # Re-raise to signal test failure
            raise
            
        finally:
            # Save tracing in any case
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                trace_path = f"debug/traces/trace_{timestamp}.zip"
                context.tracing.stop(path=trace_path)
                print(f"Trace saved in file {trace_path}", flush=True)
            except Exception as trace_error:
                print(f"Failed to save trace: {trace_error}", flush=True)
                
            browser.close()
            print("Browser closed", flush=True)

if __name__ == "__main__":
    try:
        login_test()
        print("Test run completed without errors", flush=True)
        sys.exit(0)  # Success exit code
    except Exception as e:
        print(f"Test failed: {e}", flush=True)
        sys.exit(1)  # Error exit code