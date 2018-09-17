from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import time

url = "https://preplogin.cbs.nl/"

driver = webdriver.Firefox()

t1 = time()
print(t1)
driver.get(url)
t2 = time()
print(t2)
print(t2-t1)



