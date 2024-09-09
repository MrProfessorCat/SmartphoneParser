from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.chrome.service import Service
from webdriver_manager.firefox import GeckoDriverManager
# from webdriver_manager.chrome import ChromeDriverManager


def scroll_down():
    SCROLL_CMD = 'window.scrollTo(0, document.body.scrollHeight);'
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script(SCROLL_CMD)
        sleep(3)
        new_height = driver.execute_script(SCROLL_CMD)
        if new_height == last_height:
            break
        last_height = new_height


service = Service(executable_path=GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)
# service = Service(executable_path=ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service)

driver.get('https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating&type=49659') # noqa E501
driver.maximize_window()
sleep(4)
driver.refresh()
sleep(4)
scroll_down()
sleep(4)


driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

products = driver.find_elements(
    By.CSS_SELECTOR, 'div.widget-search-result-container div.o2j_23'
)

for product in products:
    product_type = product.find_element(
        By.CSS_SELECTOR, 'span.tsBody400Small font')
    print(product_type)
