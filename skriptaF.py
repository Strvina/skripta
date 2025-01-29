import threading
import logging
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Account data
accounts = [
    {"username": " ", "password": ""}
    
]

base_url = "https://www.mozzartbet.com/sr/bonus-code"

drivers = {}

def login_to_account(account):

    driver = webdriver.Firefox(service=Service(r"C:\\geckodriver\\geckodriver.exe"))
    drivers[account["username"]] = driver

    try:
        driver.get(base_url)

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login-username"))).send_keys(account["username"])
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login-password"))).send_keys(account["password"])
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Prijavi se')]"))).click()

        logging.info(f"Account {account['username']} je uspesno ulogovan")

    except Exception as e:
        logging.error(f"Error {account['username']}: {str(e)}", exc_info=True)
        driver.quit()
        del drivers[account["username"]]


def activate_bonus(account, bonus_code):
    driver = drivers.get(account["username"])

    try:
        bonus_input_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "bonusCode")))
        bonus_input_field.send_keys(bonus_code)

        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "m-button.bonus-code-btn.medium")))
        submit_button.click()

        message_paragraph = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[@class='message center']"))
        )
        logging.info(f"Account {account['username']}: {message_paragraph.text}")

        close_icon=driver.find_element(By.CLASS_NAME, "close-icon")
        driver.execute_script("arguments[0].click();", close_icon)

        bonus_input_field = driver.find_element(By.ID, "bonusCode")
        driver.execute_script("arguments[0].click();", bonus_input_field)
        bonus_input_field.send_keys(Keys.CONTROL, "a")
        bonus_input_field.send_keys(Keys.BACKSPACE)

    except Exception as e:
        logging.error(f"Eror pri unosu koda {account['username']}: {str(e)}", exc_info=True)
    
       
def main():
    login_threads = []

    for account in accounts:
        thread = threading.Thread(target=login_to_account, args=(account,))
        login_threads.append(thread)
        thread.start()

    for thread in login_threads:
        thread.join()


    while True:
        bonus_code = input("Enter a bonus code (gasi): ")
        if bonus_code.lower() == "gasi":
            break

        bonus_threads = []
        for account in accounts:
            thread = threading.Thread(target=activate_bonus, args=(account, bonus_code))
            bonus_threads.append(thread)
            thread.start()

        for thread in bonus_threads:
            thread.join()

    for driver in drivers.values():
        driver.quit()


if __name__ == "__main__":
    main()
