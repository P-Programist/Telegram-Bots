from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options


options = Options()
options.headless = True
options.add_argument('--headless')
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
driver.get("http://www.python.org")

btn = driver.find_element_by_id('gwt-uid-3')

driver.close()