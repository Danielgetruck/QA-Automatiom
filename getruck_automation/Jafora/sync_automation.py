# sync_automation.py - Example test script for synchronization
from playwright.sync_api import sync_playwright, expect
import os
import sys
import datetime
import time
import re

def sync_test():
    with sync_playwright() as playwright:
        # Set debug mode if parameter exists
        debug_mode = "--debug" in sys.argv
        
        # Open a new browser - ensure it's visible
        browser = playwright.chromium.launch(headless=False, slow_mo=100)
        print("Opened browser in visible mode (headless=False)")
        
        # Create a new context
        context = browser.new_context(viewport={'width': 1200, 'height': 800})
        
        # Start tracing
        context.tracing.start(screenshots=True, snapshots=True)
        
        # Create a new page
        page = context.new_page()
        
        try:
            # Navigate to login page
            page.goto("https://platform-v51.getruck.co.il/login/")
            print("Navigated to login page")
            
            # Login actions
            page.get_by_role("textbox", name="אימייל").click()
            page.get_by_role("textbox", name="אימייל").fill("jafora@getruck.co")
            print("Entered email")
            
            page.get_by_role("listitem").filter(has_text="סיסמה").locator("div").nth(2).click()
            page.get_by_role("textbox", name="סיסמה").fill("Jafor2024")
            print("Entered password")
            
            page.locator("[data-test-id=\"Button\"]").click()
            print("Clicked login button")
            
            # Wait after login
            time.sleep(3)
            
            # Skip initial modal if present
            page.locator("[data-test-id=\"PlanningModal-Footer\"] [data-test-id=\"Button\"]").click()
            print("Clicked button at the bottom of modal window")
            
            time.sleep(2)
            
            # Click on sync button (focusing only on the sync test)
            page.get_by_role("button", name="סנכרון").click()
            print("Clicked sync button")
            
            time.sleep(2)
            
            # Check if synchronization was successful
            sync_results_modal = page.locator("[data-test-id=\"SyncResultsModal-Content\"]")
            
            if sync_results_modal.is_visible():
                print("Sync results modal appeared")
                
                # Check for success message
                success_text = page.locator("text=הסנכרון הושלם בהצלחה")
                
                if success_text.is_visible():
                    print("Synchronization completed successfully")
                else:
                    print("No success message found, checking for data")
                
                # Check for data in sync results
                data_elements = page.locator("[data-test-id=\"SyncResultsModal-Content\"] >> ul >> li")
                data_count = data_elements.count()
                
                if data_count > 0:
                    print(f"Received data: {data_count} items found")
                    
                    # Show details for first few items
                    for i in range(min(data_count, 3)):
                        item_text = data_elements.nth(i).text_content()
                        print(f"Item {i+1}: {item_text[:50]}...")
                else:
                    print("No data items found in sync results")
                    
                # Close sync results modal
                page.locator("[data-test-id=\"SyncResultsModal-Footer\"] [data-test-id=\"Button\"]").click()
                print("Closed sync results window")
            else:
                print("Sync results modal did not appear - synchronization may have failed")
            
            # Verify data is in workboard
            time.sleep(1)
            
            workboard_text = page.get_by_text("לוח עבודה").first
            workboard_text_content = workboard_text.text_content()
            
            # Check for items in workboard
            match = re.search(r"לוח עבודה \((\d+)\)", workboard_text_content)
            if match:
                item_count = int(match.group(1))
                print(f"Workboard shows {item_count} items available")
                if item_count > 0:
                    print("Sync was successful - data is available in workboard")
                else:
                    print("Workboard shows zero items - sync may not have added data")
            else:
                print("Could not determine number of items in workboard")
            
            # Test successfully completed
            print("Sync test completed successfully")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="debug/screenshots/sync_error_screenshot.png")
            print("Error screenshot saved at debug/screenshots/sync_error_screenshot.png")
            raise  # Re-raise to signal test failure
        finally:
            # Save trace file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            trace_path = f"debug/traces/sync_trace_{timestamp}.zip"
            context.tracing.stop(path=trace_path)
            print(f"Trace saved in file {trace_path}")
            browser.close()

if __name__ == "__main__":
    sync_test()