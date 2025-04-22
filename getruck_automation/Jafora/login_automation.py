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
        print("Opened browser in visible mode (headless=False)")
        
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
            print("Navigated to login page")
            
            # Additional wait to ensure page is loaded
            time.sleep(2)  # Wait for 2 seconds
            
            # If in debug mode, pause here and open Inspector
            if debug_mode:
                print("Debug mode active - Click continue in the Inspector window to proceed")
                page.pause()
            
            # Login actions
            page.get_by_role("textbox", name="אימייל").click()
            page.get_by_role("textbox", name="אימייל").fill("jafora@getruck.co")
            print("Entered email")
            
            page.get_by_role("listitem").filter(has_text="סיסמה").locator("div").nth(2).click()
            page.get_by_role("textbox", name="סיסמה").fill("Jafor2024")
            print("Entered password")
            
            time.sleep(1)  # Short wait before clicking
            
            page.locator("[data-test-id=\"Button\"]").click()
            print("Clicked login button")
            
            # Wait after login
            time.sleep(3)
            
            page.locator("[data-test-id=\"PlanningModal-Footer\"] [data-test-id=\"Button\"]").click()
            print("Clicked button at the bottom of modal window")
            
            time.sleep(2)
            
            # New actions you added
            page.locator("[data-test-id=\"CreatePlan-Modal-Ul-Input\"]").click()
            page.locator("[data-test-id=\"CreatePlan-Modal-Ul-Input\"]").fill("דניאל בדיקות")
            print("Entered name: Daniel Tests")
            
            time.sleep(1)
            
            page.locator("[data-test-id=\"CreatePlanModal-Ul-DatePicker-picker\"]").click()
            time.sleep(1)
            page.get_by_role("cell", name="21").first.dblclick()
            print("Selected date 21")
            
            time.sleep(1)
            
            # Branch selection - new action you added
            page.locator("#modal [data-test-id=\"Drop-Down\"]").get_by_role("list").get_by_text("סניף").click()
            print("Clicked branch selection")
            
            time.sleep(1)
            
            page.get_by_text("סניף 70").click()
            print("Selected branch 70")
            
            time.sleep(1)
            
            page.locator("[data-test-id=\"CreatePlanModal-NewButton\"]").click()
            print("Clicked new creation button")
            
            time.sleep(2)
            
            page.get_by_role("button", name="סנכרון").click()
            print("Clicked sync button")
            
            time.sleep(2)
            
            # Check if synchronization was successful
            # Wait for the sync results modal to appear
            sync_results_modal = page.locator("[data-test-id=\"SyncResultsModal-Content\"]")
            
            if sync_results_modal.is_visible():
                print("Sync results modal appeared")
                
                # Check for success message or data indicators
                success_text = page.locator("text=הסנכרון הושלם בהצלחה")
                data_elements = page.locator("[data-test-id=\"SyncResultsModal-Content\"] >> ul >> li")
                data_count = data_elements.count()
                
                if success_text.is_visible():
                    print("Synchronization completed successfully")
                else:
                    print("No success message found, checking for data")
                
                if data_count > 0:
                    print(f"Received data: {data_count} items found")
                    
                    # Optional: Get specific data details
                    for i in range(min(data_count, 3)):  # Show details for first 3 items
                        item_text = data_elements.nth(i).text_content()
                        print(f"Item {i+1}: {item_text[:50]}...")  # Print first 50 chars
                else:
                    print("No data items found in sync results")
            else:
                print("Sync results modal did not appear - synchronization may have failed")
            
            time.sleep(1)
            
            page.locator("[data-test-id=\"SyncResultsModal-Footer\"] [data-test-id=\"Button\"]").click()
            print("Clicked button at the bottom of sync results window")
            
            time.sleep(1)
            
            # Check if workboard contains data after sync
            workboard_text = page.get_by_text("לוח עבודה").first
            workboard_text_content = workboard_text.text_content()
            
            # Check if the workboard shows items (number in parentheses)
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
            
            page.get_by_text("לוח עבודה").click()
            print("Clicked workboard")
            
            time.sleep(1)
            
            # Check for routes in the route list
            routes = page.locator("[data-test-id=\"RoutePane-Routes-RoutesList-Route\"]")
            route_count = routes.count()
            
            if route_count > 0:
                print(f"Found {route_count} routes in workboard")
                # Optional: Print details of first route
                if route_count > 0:
                    first_route_text = routes.first.text_content()
                    print(f"First route: {first_route_text[:50]}...")  # Print first 50 chars
            else:
                print("No routes found in workboard")
            
            page.locator("[data-test-id=\"RoutePane-Routes-RoutesList-RouteDateSeparator\"] [data-test-id=\"Button\"]").click()
            print("Clicked button in route date separator")
            
            time.sleep(1)
            
            page.get_by_role("button", name="שמור וסגור").click()
            print("Clicked save and close")
            
            time.sleep(1)
            
            page.get_by_role("button", name="אשקלון-חדש BOOM").click()
            print("Clicked Ashkelon-New BOOM button")
            
            time.sleep(1)
            
            try:
                page.locator("._overlay_1tvvg_680").click()
                page.locator("._overlay_1tvvg_680").click()
                print("Clicked overlay element")
            except Exception as click_error:
                print(f"Failed to click overlay: {click_error}")
            
            # Save screenshot for success documentation
            page.screenshot(path="debug/screenshots/success_screenshot.png")
            print("Run completed successfully")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="debug/screenshots/error_screenshot.png")
            print("Error screenshot saved at debug/screenshots/error_screenshot.png")
        finally:
            # Ask user if they want to close the browser
            input("Press Enter to close the browser...")
            
            # Save tracing in any case
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            trace_path = f"debug/traces/trace_{timestamp}.zip"
            context.tracing.stop(path=trace_path)
            print(f"Trace saved in file {trace_path}")
            browser.close()

if __name__ == "__main__":
    login_test()