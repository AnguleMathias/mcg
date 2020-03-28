import csv
import re
import time
import gspread

from bs4 import BeautifulSoup
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import custom_logger, paste_csv_to_wks

CURRENT_DIR = "."
WINDOW_SIZE = "1024,2080"
URL = "https://www.mcg.com/care-guidelines/care-guidelines/"

current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
filename = f"{CURRENT_DIR}/logs/scraped_{current_time}.log"

logger = custom_logger(filename)

logger.info(f"Log file name {filename}")

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
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "layer__content"))
    )
except TimeoutException as err:
    logger.info("Page did not fully load in due time. Trying again")
    failed = True
    tries = 0
    while failed:
        try:
            elem = WebDriverWait(driver, 10).until(
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
wr = csv.writer(fp, dialect="excel")
wr.writerow(["article", "p"])

logger.info(f"Writing data to {csv_path}...")

while True:
    time.sleep(3)
    try:
        line = []
        article = driver.find_element_by_xpath(
            "/html/body/main/section/div/div/article"
        ).text
        line.append(article)

        p = driver.find_element_by_xpath(
            "/html/body/main/section/div/div/article/p"
        ).text
        p = BeautifulSoup(p, "lxml").text
        cleaner = re.compile("<.*?>")
        cleaned_text = re.sub(cleaner, "", p)
        line.append(cleaned_text)

        wr = csv.writer(fp, dialect="excel")
        wr.writerow(line)

        driver.find_element_by_xpath("/html/body/main/section/div/div/article/h3[1]")
        break

        logger.info(f"Writing data to {csv_path}...")

    except NoSuchElementException:
        fp.close()

content = open(csv_path, "r", encoding="utf-8").read()

logger.info("Write csv content to mcg googlesheet")

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    f"{CURRENT_DIR}/mcg-scraper-fb4e0f7c974e.json", scope
)

gc = gspread.authorize(credentials)
wks = gc.open("mcg")
paste_csv_to_wks(csv_path, wks, "A2")

logger.info("Writing complete!")

driver.quit()
