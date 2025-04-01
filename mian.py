from playwright.sync_api import sync_playwright, Page
import time

def login_test():
    with sync_playwright() as playwright:
        # הפעלת דפדפן 
        browser = playwright.chromium.launch(headless=False, slow_mo=100)
        
        # יצירת דף חדש
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # ניווט לדף הכניסה
        page.goto("https://platform-dev.getruck.co.il/login/")
        print("נכנס לדף הכניסה")
        
        # המתנה לטעינת הדף
        page.wait_for_load_state("networkidle")
        
        # הזנת פרטי כניסה - שם משתמש וסיסמה
        # משתמש בסלקטורים המדויקים על פי הקוד שסיפקת
        page.get_by_role('textbox', name='אימייל').click()
        page.get_by_role('textbox', name='אימייל').fill("jafora@getruck.co")
        
        page.get_by_role('textbox', name='סיסמה').click()
        page.get_by_role('textbox', name='סיסמה').fill("Jafor2024")
        print("הוזנו פרטי התחברות")
        
        # לחיצה כפולה על כפתור הכניסה
        page.locator('[data-test-id="Button"]').dblclick()
        print("בוצעה לחיצה על כפתור הכניסה")
        
        # המתנה לניווט אחרי ההתחברות
        page.wait_for_load_state("networkidle")
        
        # המתנה של 5 שניות
        time.sleep(5)
        print("הושלמה התחברות")
        
        # לחיצה על כפתור עם data-test-id="PlanningModal-Footer"
        page.locator('[data-test-id="PlanningModal-Footer"] [data-test-id="Button"]').click()
        print("לחיצה על כפתור בחלק התחתון של המודאל")
        
        # המתנה קצרה
        time.sleep(2)
        
        # מילוי שדה הקלט בחלון החדש
        input_field = page.locator('[data-test-id="CreatePlan-Modal-Ul-Input"]')
        input_field.click()
        input_field.fill("דניאל בדיקות")
        print("הוזן טקסט: דניאל בדיקות")
        
        # בחירת תאריך
        page.get_by_text('02/04/').click()
        time.sleep(1)
        
        # לחיצה כפולה על תא עם התאריך הרצוי
        page.get_by_role('cell', name='2', exact=True).first.dblclick()
        print("נבחר תאריך")
        
        # המתנה לאחר בחירת התאריך
        time.sleep(2)
        
        # בחירת סניף
        # קודם לוחץ על בורר הסניף
        page.locator('span').filter(has_text='סניף 30').first.click()
        time.sleep(1)
        
        # בוחר את סניף 70 מהרשימה
        page.get_by_text('סניף 70').click()
        print("נבחר סניף 70")
        
        # המתנה לאחר בחירת הסניף
        time.sleep(2)
        
        # לחיצה על כפתור יצירה
        page.locator('[data-test-id="CreatePlanModal-NewButton"]').click()
        print('לחיצה על כפתור "צור חדש"')
        
        # המתנה של 5 שניות
        time.sleep(5)
        
        # לחיצה על כפתור סנכרון
        page.get_by_role('button', name='סנכרון').click()
        print('לחיצה על כפתור "סנכרון"')
        
        # המתנה קצרה
        time.sleep(1)
        
        # ***** הוספת קוד הזזת העכבר ב-2 ס"מ ימינה *****
        # קבלת מיקום נוכחי של העכבר
        current_position = page.evaluate('''() => { 
            return {
                x: window.innerWidth / 2,
                y: window.innerHeight / 2
            }
        }''')
        current_x = current_position['x']
        current_y = current_position['y']
        
        # המרת 2 ס"מ לפיקסלים (בערך 38 פיקסלים = 1 ס"מ)
        pixels_per_cm = 38
        pixels_to_move = 2 * pixels_per_cm  # 2 ס"מ
        
        # הזזת העכבר ימינה ב-2 ס"מ
        new_x = current_x + pixels_to_move
        page.mouse.move(new_x, current_y)
        print(f"העכבר זז {pixels_to_move} פיקסלים ימינה")
        
        # המתנה קצרה לראות את התנועה
        time.sleep(1)
        # ***** סוף קוד הזזת העכבר *****
        
        # לחיצה על כפתור בתחתית מודאל תוצאות הסנכרון
        page.locator('[data-test-id="SyncResultsModal-Footer"] [data-test-id="Button"]').click()
        print('לחיצה על כפתור בתחתית מודאל תוצאות הסנכרון')
        
        # המתנה קצרה
        time.sleep(2)
        
        # לחיצה על "לוח עבודה (2)"
        page.get_by_text('לוח עבודה (2)').click()
        print('לחיצה על "לוח עבודה (2)"')
        
        # המתנה קצרה
        time.sleep(2)
        
        # לחיצה על כפתור במפריד תאריך מסלול
        page.locator('[data-test-id="RoutePane-Routes-RoutesList-RouteDateSeparator"] [data-test-id="Button"]').click()
        print('לחיצה על כפתור במפריד תאריך מסלול')
        
        # המתנה קצרה
        time.sleep(2)
        
        # לחיצה על כפתור "שמור והוסף נהג חדש"
        page.get_by_role('button', name='שמור והוסף נהג חדש').click()
        print('לחיצה על כפתור "שמור והוסף נהג חדש"')
        
        # המתנה קצרה
        time.sleep(2)
        
        # לחיצה על כפתור מסלול רמי לוי
        page.get_by_role('button', name='רמי לוי אילת -ב.ה לוי בע"מ מ: באר שבע ל: , אילת איזור סחר חופשי').click()
        print('לחיצה על כפתור מסלול רמי לוי')
        
        # המתנה של 5 שניות
        time.sleep(5)
        
        # צילום מסך סופי
        page.screenshot(path="final_result.png")
        print("בוצע צילום מסך סופי")
        
        # סגירת הדפדפן
        browser.close()
        print("הדפדפן נסגר")

if __name__ == "__main__":
    login_test()