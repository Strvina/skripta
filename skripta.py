import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytesseract
from io import BytesIO
from PIL import Image
import requests
import logging
import os

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Account data
accounts = [
    {"username": "", "password": ""}
    
]

# Base URL
base_url = "https://www.mozzartbet.com/sr/mozz-app"

# Set the path for Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function for login
def login(driver, username, password):
    driver.get(base_url)
    prijava_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "login-btn")))
    prijava_link.click()
    username_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login-username")))
    username_input.send_keys(username)
    password_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login-password")))
    password_input.send_keys(password)
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Prijavi se')]")))
    login_button.click()
    WebDriverWait(driver, 10).until(EC.url_changes(base_url))

# Function to navigate to the third conversation card
def navigate_to_conversation(driver):
    conversation_cards = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "MozzAppConversationCard"))
    )
    if len(conversation_cards) >= 3:
        conversation_cards[2].click()

# Function to extract text from an image
def monitor_and_copy_text(driver):
    image_element = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CLASS_NAME, "MozzAppPromotionCard__image--first-message-other-user"))
    )
    image_url = image_element.get_attribute('src')
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    cropped_img = img.crop((2, 170, 246, 202))  # Adjust crop dimensions
    return pytesseract.image_to_string(cropped_img)

# Function to perform actions after extracting text
def perform_steps(driver, extracted_text):
    try:
        # Navigate to bonus code input page
        messages_icon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "link-icon.user-outlined.svg.svg__messages-outlined")))
        messages_icon.click()
        time.sleep(2)
        bonus_code_icon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "link-icon.svg.svg__bonus_code_enter_page")))
        bonus_code_icon.click()
        time.sleep(2)
        
        # Enter the bonus code
        bonus_input_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "form__input.text")))
        bonus_input_field.send_keys(extracted_text)
        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "m-button.bonus-code-btn.medium")))
        submit_button.click()
        
        # Wait for the message center paragraph to appear
        message_paragraph = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "message-center"))
        )
        message_text = message_paragraph.text
        
        # Save the message text to a file
        file_path = os.path.join(os.path.dirname(__file__), "message_center_texts.txt")
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"{message_text.strip()}\n")
        
        logging.info(f"Extracted and saved message: {message_text}")
        return True
    except Exception as e:
        logging.error(f"Error during steps: {str(e)}")
        return False


# Function to handle individual account workflow
def handle_account(account):
    while True:
        driver = webdriver.Chrome(service=Service(r'C:\chromedriver-win64\chromedriver.exe'))
        driver.maximize_window()
        try:
            logging.info(f"Processing account: {account['username']}")
            login(driver, account["username"], account["password"])
            navigate_to_conversation(driver)
            
            # Monitor and copy text
            text = monitor_and_copy_text(driver)
            
            if text:
                # Perform steps after extracting text
                success = perform_steps(driver, text)
                
                if success:
                    logging.info(f"Bonus code successfully submitted for {account['username']}. Retrying process...")
                else:
                    logging.warning(f"Failed to submit bonus code for {account['username']}. Retrying process...")
                
                # Restart the loop immediately for this thread
                continue
            
        except Exception as e:
            logging.error(f"Error for account {account['username']}: {str(e)}")
        finally:
            driver.quit()

        # Sleep for a specific time before relogging (if no immediate re-run is needed)
        logging.info(f"Retrying for {account['username']}...")
         # Wait 5 minutes


# Start threads for each account
threads = []
for account in accounts:
    thread = threading.Thread(target=handle_account, args=(account,))
    thread.start()
    threads.append(thread)

# Join threads (optional)
for thread in threads:
    thread.join()
