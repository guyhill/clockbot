from selenium import webdriver
from time import time, localtime, sleep, strftime

import csv
import sys
import math
import argparse

csv.register_dialect("nl_excel", csv.excel, delimiter = ";")

base_url = "https://preplogin.cbs.nl/"
browsers = {
    "firefox": webdriver.Firefox,
    "chrome": webdriver.Chrome,
    "ie": webdriver.Ie,
    "edge": webdriver.Edge
}
methods = [
    "linear",
    "index"
]
xpath_menu_items_different = '//*[@id="v"]//table//tr[position() > 1]//a | //*[@id="v"]/tbody/tr/td/div/a'

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

def click_and_wait(driver, element):

    element.click()

    try:
        page = driver.find_element_by_css_selector("#x")
        #cur_contents = driver.execute_script("return arguments[0].outerHTML;", page)
        cur_contents = page.get_attribute("innerHTML")
        #print("############################################")
        #print(cur_contents)
    except:
        cur_contents = ""


    while True:
        try:
            page = driver.find_element_by_css_selector("#x")
            #contents = driver.execute_script("return arguments[0].outerHTML;", page)
            contents = page.get_attribute("innerHTML")
            #print("############################################")
            #print(contents)
            if contents != cur_contents:
                cur_contents = contents
                #log("new x")
                break
            #log("same x")
        except:
            #log("no x")
            pass
        sleep(0.01)

def startup(browser_name = "firefox"):
    log("Starting browser: " + browser_name)    
    try:
        init = browsers[browser_name]
    except KeyError: 
        log("Unknown browser: " + browser_name)
        exit(1)
    driver = init()
    log("Startup complete")
    return driver

def stop(driver):
        log("Closing browser")
        driver.close()
        log("Browser closed")

def navigate_page(url):
    log("Navigating to page: " + url)
    driver.get(url)

def login(driver, uname, pwd):
    log("Filling in username: " + uname)
    driver.find_element_by_css_selector("input#Username").send_keys(uname)
    log("Filling in password: " + pwd)
    driver.find_element_by_css_selector("input#Password").send_keys(pwd)
    log("Press login button")
    click_and_wait(driver, driver.find_element_by_css_selector("input[value='Inloggen']"))
    log("Login complete")
    active_elements = driver.find_elements_by_css_selector("#v .Font12")
    active_texts = [ element.text for element in active_elements ]
    log("Active item: " + " ".join(active_texts))

def navigate_first_menu_item(driver):
    log("Navigating to first menu item")
    click_and_wait(driver, driver.find_element_by_css_selector("#v td p"))
    log("Navigation to first menu item complete.")
    active_elements = driver.find_elements_by_css_selector("#v .Font12")
    active_texts = [ element.text for element in active_elements ]
    log("Active item: " + " ".join(active_texts))

def navigate_next(driver):
    log("Navigating to next menu item")
    try:
        element = driver.find_element_by_css_selector("#ac")
    except:
        log("No next item found")
        return False
    click_and_wait(driver, element)
    log("Navigation to next menu item complete.")
    active_elements = driver.find_elements_by_css_selector("#v .Font12")
    active_texts = [ element.text for element in active_elements ]
    log("Active item: " + " / ".join(active_texts))
    return True

def get_menu_length(driver):
    log("Getting number of menu items")
    elements = driver.find_elements_by_xpath(xpath_menu_items_different)
    n_elements = len(elements)
    log ("Found {:d} menu items".format(n_elements))
    return n_elements
    
def navigate_nth_menu_item(driver, i):
    log("Navigating to menu item " + str(i))
    elements = driver.find_elements_by_xpath(xpath_menu_items_different)
    click_and_wait(driver, elements[i])
    active_elements = driver.find_elements_by_css_selector("#v .Font12")
    active_texts = [ element.text for element in active_elements ]
    log("Navigation to menu item {:d} complete.".format(i))
    log("Active item: " + " ".join(active_texts))

def is_first_item(driver):
    element = driver.find_element_by_xpath("//*[@id='v']/tbody/tr[1]//a")
    attr = element.get_attribute("class")
    return "Font12" in attr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Measure how fast questionnaire pages load in different browsers")
    parser.add_argument("-b", dest = "browser", choices = list(browsers.keys()), default = list(browsers.keys())[0], help = "Browser name. Default: %(default)s")
    parser.add_argument("-t", dest = "traversal_method", choices = methods, default = methods[0], help = "Questionnaire traversal method. Default: %(default)s.")
    parser.add_argument(dest = "cred_fname", help = "Filename of credentials file")
    args = parser.parse_args()

    log("Clockbot start")
    creds = read_credentials(args.cred_fname)

    for cred in creds:
        driver = startup(args.browser)
        navigate_page(base_url)
        login(driver, cred["Gebruikersnaam"], cred["Wachtwoord"])
        if not is_first_item(driver):
            log("Not on first page.")
            navigate_first_menu_item(driver)
            stop(driver)
            driver = startup(args.browser)
            navigate_page(base_url)
            login(driver, cred["Gebruikersnaam"], cred["Wachtwoord"])

        if args.traversal_method == "linear":
            while navigate_next(driver):
                pass
        elif args.traversal_method == "index":
            n = get_menu_length(driver)
            for i in range(1, n):
                navigate_nth_menu_item(driver, i)
                navigate_first_menu_item(driver)
        else:
            log("Unknown traversal method " + args.traversal_method)
            log("Quitting")
            exit(1)

        stop(driver)

    log("End")
