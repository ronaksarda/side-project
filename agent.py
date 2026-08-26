from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,slow_mo=50)
    page = browser.new_page()
    
    page.goto("https://forms.gle/xXQdG4Se4Vn5tVRJ8")
    
    page.wait_for_load_state("networkidle")
    
    print("Page is now loaded noice")
    
    input("Please enter here to close the terminal")
    
    browser.close()
