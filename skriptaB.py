import sys
import threading
import logging
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


accounts = [
    {"username": "", "password": ""}
    
]

base_url = "https://www.mozzartbet.com/sr/bonus-code"

def activate_bonus(account, bonus_code):
    options = Options()
    options.headless = True

    driver = webdriver.Firefox(service=Service(r"C:\geckodriver\geckodriver.exe"), options=options)

    try:
        logging.info(f"Starting process for account: {account['username']}")
        driver.get(base_url)

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login-username"))).send_keys(account["username"])
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login-password"))).send_keys(account["password"])
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Prijavi se')]"))).click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "bonusCode")))

        bonus_input_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "bonusCode")))
        bonus_input_field.send_keys(bonus_code)

        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "m-button.bonus-code-btn.medium")))
        submit_button.click()

        message_paragraph = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[@class='message center']"))
        )
        logging.info(f"Account {account['username']}: {message_paragraph.text}")

    except Exception as e:
        logging.error(f"Error for account {account['username']}: {str(e)}", exc_info=True)
    finally:
        logging.info(f"Finishing process for account: {account['username']}")
        driver.quit()

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <bonus_code>")
        sys.exit(1)

    bonus_code = sys.argv[1]
    threads = []

    for account in accounts:
        logging.info(f"Starting thread for account: {account['username']}")
        thread = threading.Thread(target=activate_bonus, args=(account, bonus_code))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join() 
        logging.info("Thread joined successfully.")

if __name__ == "__main__":
    main()
