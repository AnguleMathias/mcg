import csv
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

# CURRENT_DIR = /Users/mathias/Desktop/mcg
CURRENT_DIR = '.'
WINDOW_SIZE = '1024,2080'
URL = 'https://www.mcg.com/about/company-overview/'
SCROLL_PAUSE_TIME = 3
EXCEPTION_SLEEP_TIME = 2

current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
filename = f'{CURRENT_DIR}/logs/scraped_{current_time}.log'

logger = custom_logger(filename)

logger.info(f'Logfile name {filename}')

# Chrome browser options - Version 79.0.3945.88 (Official Build) (64-bit)
chrome_options = Options()

# chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--mute-audio")

driver = webdriver.Chrome(
    executable_path=f'{CURRENT_DIR}/chromedriver', options=chrome_options)

logger.info("Opening page..")
driver.get(URL)
