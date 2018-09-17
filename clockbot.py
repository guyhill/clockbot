from selenium import webdriver
from time import time, localtime, sleep, strftime

import csv
import sys
import math

csv.register_dialect("nl_excel", csv.excel, delimiter = ";")

base_url = "https://preplogin.cbs.nl/"

def read_credentials(filename):
    log("Reading credentials")
    with open(filename, "r", newline = "", encoding="utf-8") as f_in:
        csvFile = csv.DictReader(f_in, dialect = "nl_excel")
        result = list(csvFile)
    log("Reading credentials complete")
    return result

def log(msg):
    t = time()
    lt = localtime(t)
    ms, _ = math.modf(t)
    ms = int(1000 * ms)
    print(strftime("%Y-%m-%d %H:%M:%S", lt) + "." + "{:03d} {:.6f}".format(ms, t),  msg)

cur_page_title = ""
def wait_for_new_page_title(driver):
    global cur_page_title

    while True:
        try:
            page_title_element = driver.find_element_by_css_selector("#x")
            page_title = driver.execute_script("return arguments[0].outerHTML;", page_title_element)
            if page_title != cur_page_title:
                cur_page_title = page_title
                break
        except:
            pass
        sleep(0.01)

def startup(starturl):
    log("Starting browser")
    driver = webdriver.Firefox()
    log("Navigating to start page")
    driver.get(starturl)

    return driver

def login(driver, uname, pwd):
    log("Filling in username: " + uname)
    driver.find_element_by_css_selector("input#Username").send_keys(uname)
    log("Filling in password: " + pwd)
    driver.find_element_by_css_selector("input#Password").send_keys(pwd)
    log("Press login button")
    driver.find_element_by_css_selector("input[value='Inloggen']").click()
    wait_for_new_page_title(driver)
    log("Login complete")

def navigate_first_menu_item(driver):
    log("Navigating to first menu item")
    driver.find_element_by_css_selector("#v td p").click()
    wait_for_new_page_title(driver)
    active_elements = driver.find_elements_by_css_selector("#v .Font12")
    active_texts = [ element.text for element in active_elements ]
    log("Navigation to first menu item complete.")
    log("Active item: " + " ".join(active_texts))

def navigate_next(driver):
    log("Navigating to next menu item")
    try:
        driver.find_element_by_css_selector("#ac").click()
    except:
        log("No next item found")
        return False
    wait_for_new_page_title(driver)
    active_elements = driver.find_elements_by_css_selector("#v .Font12")
    active_texts = [ element.text for element in active_elements ]
    log("Navigation to next menu item complete.")
    log("Active item: " + " / ".join(active_texts))
    return True


if __name__ == "__main__":
    log("Clockbot start")
    cred = read_credentials("InloggegevensVragenlijst.csv")

    driver = startup(base_url)
    login(driver, cred[0]["Gebruikersnaam"], cred[0]["Wachtwoord"])
    navigate_first_menu_item(driver)

    while navigate_next(driver):
        pass

    log("Stopping browser")
    driver.close()
    log("End")
