import csv
import re
import time

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

from utils import custom_logger

# CURRENT_DIR = /Users/mathias/Desktop/mcg
CURRENT_DIR = "."
WINDOW_SIZE = "1024,2080"
URL = "https://www.mcg.com/care-guidelines/care-guidelines/"
SCROLL_PAUSE_TIME = 3
EXCEPTION_SLEEP_TIME = 2

current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
filename = f"{CURRENT_DIR}/logs/scraped_{current_time}.log"

logger = custom_logger(filename)

logger.info(f"Logfile name {filename}")

# Chrome browser options - Version 79.0.3945.88 (Official Build) (64-bit)
chrome_options = Options()

# chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--mute-audio")

driver = webdriver.Chrome(
    executable_path=f"{CURRENT_DIR}/chromedriver", options=chrome_options
)

logger.info("Opening page..")
driver.get(URL)

try:
    logger.info("Waiting for page to load...")
    el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "layer__content"))
    )
except TimeoutException as err:
    logger.info("Page did not fully load in due time. Trying again")
    failed = True
    tries = 0
    while failed:
        try:
            el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "layer__content"))
            )
        except TimeoutException as err:
            if tries >= 10:
                logger.error(
                    "Something went wrong. Please check your internet connection"
                )
                driver.quit()
                exit()
            else:
                tries += 1
                logger.info(f"TimeoutException, retrying {tries} times...")
        else:
            failed = False

logger.info("Page loaded successfully")
time.sleep(3)

csv_path = f"{CURRENT_DIR}/csv/mcg_{current_time}.csv"
fp = open(csv_path, "w")
wr = csv.writter(fp, dialect="excel")
wr.writerow(["article", "p"])

logger.info(f"Writing data to {csv_path}...")

while True:
    time.sleep(3)
    try:
        paragraph_blocks = driver.find_element_by_xpath(
            "/html/body/main/section/div/div/article/p[1]"
        )

        for paragraph in paragraph_blocks:
            line = []
            article = paragraph.find_element_by_xpath(
                "/html/body/main/section/div/div/article"
            ).text
            line.append(article)

            p = paragraph.find_element_by_xpath(
                "/html/body/main/section/div/div/article/p"
            ).text
            p = BeautifulSoup(p, "lxml").text
            cleaner = re.compile("<.*?>")
            cleaned_text = re.sub(cleaner, "", text)
            line.append(cleaned_text)

        wr = csv.writer(fp, dialect="excel")
        wr.writerow(line)

    except NoSuchElementException:
        logger.info(f"Writing data to {csv_path}...")

        fp.close()

        break

