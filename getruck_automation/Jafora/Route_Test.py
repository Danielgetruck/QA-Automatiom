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
            
            # Check for trucks/vehicles in the workboard
            try:
                # Look for elements that indicate trucks were added
                truck_indicators = [
                    "[data-test-id=\"RoutePane-Routes-RoutesList-Route-Truck\"]",
                    "[data-test-id=\"RoutePane-Routes-RoutesList-Route-Vehicle\"]",
                    "[data-test-id=\"Vehicle-Label\"]",
                    "text=משאית",
                    "text=רכב"
                ]
                
                trucks_found = False
                for indicator in truck_indicators:
                    try:
                        truck_elements = page.locator(indicator)
                        if truck_elements.count() > 0:
                            truck_count = truck_elements.count()
                            print(f"Found {truck_count} trucks/vehicles in workboard")
                            trucks_found = True
                            
                            # Get details of first truck if found
                            if truck_count > 0:
                                first_truck_text = truck_elements.first.text_content()
                                print(f"First truck/vehicle: {first_truck_text[:50]}...")
                            
                            break
                    except Exception as truck_error:
                        print(f"Error checking for truck indicator {indicator}: {truck_error}")
                
                if trucks_found:
                    print("SUCCESS: Trucks/vehicles were successfully added!")
                    print("Test completed successfully - trucks were added")
                    
                    # Take a screenshot of successful state
                    page.screenshot(path="debug/screenshots/trucks_added_success.png")
                    print("Saved screenshot of successful trucks addition")
                    
                    # Test can be completed here if trucks were found
                    print("All success criteria met - test completed")
                else:
                    print("No trucks/vehicles found yet - continuing with additional steps")
            except Exception as truck_check_error:
                print(f"Error during truck verification: {truck_check_error}")
                print("Continuing with test...")
            
        
                if trucks_found:
                    print("SUCCESS: Trucks/vehicles were successfully added after overlay interaction!")
                    print("Test completed successfully - trucks were added")
                else:
                    print("Still no trucks/vehicles found - further steps may be needed")
            except Exception as final_check_error:
                print(f"Error during final truck verification: {final_check_error}")
            
            # Save screenshot for success documentation
            page.screenshot(path="debug/screenshots/success_screenshot.png")
            print("Run completed successfully")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="debug/screenshots/error_screenshot.png")
            print("Error screenshot saved at debug/screenshots/error_screenshot.png")
        finally:
            # Save tracing before closing browser
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            trace_path = f"debug/traces/trace_{timestamp}.zip"
            context.tracing.stop(path=trace_path)
            print(f"Trace saved in file {trace_path}")
            
            # Automatic browser close instead of asking for user input
            print("Closing browser automatically...")
            browser.close()
            print("Browser closed - test execution complete")

if __name__ == "__main__":
    login_test()