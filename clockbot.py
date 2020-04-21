#
# Clockbot
#
# (c) 2018 Centraal Bureau voor de Statistiek / Statistics Netherlands
#
# Author: Guido van den Heuvel
#
# This program automatically navigates an entire CBS questionnaire and collects
# timing information of page loads
#
# Change log:
# 19 sep 2018: creation
#
import csv
import sys
import os
import math
import argparse
from time import time, localtime, sleep, strftime
from importlib import import_module
import json

from selenium import webdriver
from selenium.common.exceptions import *

# Force csv to write file in Dutch csv format (i.e., use ; as field delimiters).
# But note that the Python csv standard library does not support commas as decimal separators.
csv.register_dialect("nl_excel", csv.excel, delimiter = ";")

# Url of the login screen
base_url = "https://preplogin.cbs.nl/"

# List of supported browsers
# Note: I did not test Edge, since I developed this on a Windows 7 machine. Edge only runs on Windows 10
browsers = {
    "firefox": webdriver.Firefox,
    "chrome": webdriver.Chrome,
    "ie": webdriver.Ie,
    "edge": webdriver.Edge
}

# List of traversal methods. "Linear" starts with the first page and repeatedly pushes the "Next page"
# button until the last page is reached. "Index" traverses all pages that can be reached from the menu bar
# by clicking each menu item in turn and returning to the first page afterwards
methods = [
    "linear",
    "index"
]

log_file = sys.stdout

def parse_arguments():
    """
    Parse the command line arguments. See code for details on arguments, and names of variables in which argument values are stored
    (not repeated here to avoid the risk of comment and code becoming inconsistent)

    Returns: the arguments, parsed
    """
    parser = argparse.ArgumentParser(description = "Measure how fast questionnaire pages load in different browsers")
    parser.add_argument(dest = "cred_filename", help = "Filename of credentials file")
    parser.add_argument("-b", dest = "browser", choices = list(browsers.keys()), default = list(browsers.keys())[0], help = "Browser name. Default: %(default)s")
    parser.add_argument("-t", dest = "traversal_method", choices = methods, default = methods[0], help = "Questionnaire traversal method. Default: %(default)s.")
    parser.add_argument("-o", dest = "output_filename", default = None, help = "Filename of output file. Default: dump to console.")
    parser.add_argument("-n", dest = "n_runs", type = int, default = 1, help = "Number of runs for each questionnaire. Default: %(default)i.")
    parser.add_argument("-c", dest = "config", default = "ps2", help = "Configuration to use. Default: %(default)s.")
    args = parser.parse_args()

    return args

def read_credentials(filename):
    """
    Read a file with user names and passwords. This file must be a csv file, with ; as separators. The csv
    file is assumed to have column headers in the first row, and at least the columns "Gebruikersnaam" (username)
    and "Wachtwoord" (password) must be present

    filename: (string) name of the file with credentials

    return value: the contents of the CSV file as a list. Each item on the list represents one record, with each field
    one value of an OrderedDict
    """
    log("Reading credentials")
    with open(filename, "r", newline = "", encoding="utf-8") as f_in:
        csvFile = csv.DictReader(f_in, dialect = "nl_excel")
        result = list(csvFile)
    log("Reading credentials complete")
    return result

def log_init(filename):
    global log_file

    if filename is not None:
        log_file = open(filename, "w", encoding = "utf-8", buffering = 1)

def log(msg):
    """
    logs a message to the log file. The message is preceded by human-readable date & time, and timestamp in machine-friendly format.
    The data & time on the one hand, and the timestamp on the other, are guaranteed to be the same moment, up to the same
    millisecond

    msg: (string) the message to log
    """
    t = time()
    lt = localtime(t)
    ms, _ = math.modf(t)
    ms = int(1000 * ms)
    log_file.write(strftime("%Y-%m-%d %H:%M:%S", lt) + "." + "{:03d} {:.6f}".format(ms, t) + " " + msg + "\n")
    log_file.flush()
    if log_file.fileno() != 1: # don't fsync stdout
        os.fsync(log_file.fileno())

def click_and_wait_contents(driver, element):
    """
    Clicks the given element, and wait for the page to load. Waiting for page load is a tricky proposition for which no standard
    method exists that is guaranteed to work in all circumstances. For CBS questionnaires, we have found that the following works,
    seemingly in all cases: 

    1. Store the text of the questionnaire page
    2. Click the element
    3. Repeatedly store the text of the questionnaire page until this text is different from the text stored before clicking

    driver: webdriver instance
    element: webdriver element instance; element on the web page that is to be clicked
    """
    try:
        page = driver.find_element_by_css_selector(css_wait_full_page)
        cur_contents = page.get_attribute("textContent")
    except:
        cur_contents = ""

    try:
        element.click()
    except (
        ElementClickInterceptedException, 
        ElementNotInteractableException, 
        ElementNotVisibleException) as e:

        log(f"{e}: Element cannot be clicked")
        driver.save_screenshot("screenshot.png")
        return

    while True:
        try:
            page = driver.find_element_by_css_selector(css_wait_full_page)
            contents = page.get_attribute("textContent")
            if contents != cur_contents:
                cur_contents = contents
                break
        except:
            pass
        sleep(0.01)


def click_and_wait_ie(driver, element):
    """
    Clicks the given element, and wait for the page to load. Waiting for page load is a tricky proposition for which no standard
    method exists that is guaranteed to work in all circumstances. For CBS questionnaires, we have found that the following works,
    seemingly in all cases: 

    1. Store the text of the questionnaire page
    2. Click the element
    3. Repeatedly store the text of the questionnaire page until this text is different from the text stored before clicking

    driver: webdriver instance
    element: webdriver element instance; element on the web page that is to be clicked
    """
    try:
        page = driver.find_element_by_css_selector(css_wait_full_page)
        cur_contents = page.get_attribute("textContent")
    except:
        cur_contents = ""

    try:
        element.click()
    except (
        ElementClickInterceptedException, 
        ElementNotInteractableException, 
        ElementNotVisibleException) as e:

        log(f"{e}: Element cannot be clicked")
        driver.save_screenshot("screenshot.png")
        return

    while True:
        try:
            page = driver.find_element_by_css_selector(css_wait_full_page)
            contents = page.get_attribute("textContent")
            if contents != cur_contents:
                cur_contents = contents
                break
        except:
            pass
        sleep(0.01)
    while True:
        try:
            splash = driver.find_element_by_css_selector(".splash-active")
            #print(f"Splash still found. Visible: {splash.is_displayed()}")
        except:
            #print("splash disappeared")
            break
        sleep(0.01)


def click_and_wait_splash(driver, element):
    """
    Necessary for Blaise 5.5.8. In that Blaise version the "splash screen" (blank screen with progress bar)
    stays visible on top of the page contents for a few tenths of seconds, with the result that menu items
    are on the page but not clickable because they are obscured by the splash screen. Simply waiting for the
    splash screen to appear and then disappear does the trick for this version. However, this does not work
    for Blaise 5.2.5
    """ 
    try:
        element.click()
    except (
        ElementClickInterceptedException, 
        ElementNotInteractableException, 
        ElementNotVisibleException) as e:

        log(f"{e}: Element cannot be clicked")
        return

    while True:
        try:
            splash = driver.find_element_by_css_selector(".splash-active")
            #print(f"Splash found. Visible: {splash.is_displayed()}")
            break
        except:
            #print("splash not found")
            pass
        sleep(0.01)

    while True:
        try:
            splash = driver.find_element_by_css_selector(".splash-active")
            #print(f"Splash still found. Visible: {splash.is_displayed()}")
        except:
            #print("splash disappeared")
            break
        sleep(0.01)

    

def startup(browser_name = "firefox"):
    """
    Starts a browser and returns the associated webdriver instance

    browser_name (string): name of the browser. Must be one of the keys of the "browsers" dict

    Returns: webdriver instance
    """
    log("Starting browser: " + browser_name)    
    try:
        init = browsers[browser_name]
    except KeyError: 
        log("Unknown browser: " + browser_name)
        exit(1)
    driver = init()
    driver.maximize_window()
    log("Startup complete")
    return driver

def stop(driver):
    """
    Stops the browser associated with driver

    driver: webdriver instance
    """
    log("Closing browser")
    driver.close()
    log("Browser closed")

def navigate_page(driver, url):
    """
    Navigates the browser associated with driver to the given url

    driver: webdriver instance
    url (string): URL to navigate to
    """
    log("Navigating to page: " + url)
    driver.get(url)

def login(driver, uname, pwd):
    """
    Enters login details in the current page of the browser associated with driver
    """
    log("Filling in username: " + uname)
    driver.find_element_by_css_selector(css_username_field).send_keys(uname)
    log("Filling in password: " + pwd)
    driver.find_element_by_css_selector(css_password_field).send_keys(pwd)
    log("Pressing login button")
    click_and_wait(driver, driver.find_element_by_css_selector(css_login_button))
    log("Login complete")
    active_elements = driver.find_elements_by_css_selector(css_menu_active_font)
    active_texts = [ element.text for element in active_elements ]
    log("Active item: " + " / ".join(active_texts))

def navigate_first_menu_item(driver):
    """
    Navigates to the first page of the questionnaire, which is supposed to be the active page of the
    browser associated with driver

    driver: webdriver instance
    """
    log("Navigating to first menu item")
    click_and_wait(driver, driver.find_element_by_css_selector(css_menu_items))
    log("Navigation complete")
    active_elements = driver.find_elements_by_css_selector(css_menu_active_font)
    active_texts = [ element.text for element in active_elements ]
    log("Active item: " + " / ".join(active_texts))

def navigate_next(driver):
    """
    Navigate to the next page of the questionnaire, using the "next page" / "volgende" button. The
    questionnaire is assumed to be the active page of the browser associated with driver

    driver: webdriver instance. 
    """
    log("Navigating to next menu item")
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    try: 
        driver.execute_script(f"elt=document.getElementById('{id_scrollbar_item}');elt.scrollTo(0, elt.scrollHeight);")
    except:
        pass

    try:
        element = driver.find_element_by_css_selector(css_next_page_button)
    except:
        log("No next item found")
        return False
    click_and_wait(driver, element)
    log("Navigation complete")
    active_elements = driver.find_elements_by_css_selector(css_menu_active_font)
    active_texts = [ element.text for element in active_elements ]
    log("Active item: " + " / ".join(active_texts))
    return True

def get_menu_length(driver):
    """
    Finds the number of items in the sidebar menu of the questionnaire. This is assumed to be
    the active document in the browser associated with driver

    driver: webdriver instance

    returns: the number of menu items found
    """
    log("Getting number of menu items")
    elements = driver.find_elements_by_css_selector(css_menu_items)
    n_elements = len(elements)
    log ("Found {:d} menu items".format(n_elements))
    return n_elements
    
def navigate_nth_menu_item(driver, i):
    """
    Navigates to the nth item in the sidebar menu of the questionnaire. This is assumed to be
    the active document in the browser associated with driver

    driver: webdriver instance
    i (integer): number of the menu item that is navigated to. This is zero-based, i.e., 0 is the first menu item
    """
    log("Navigating to menu item " + str(i))
    elements = driver.find_elements_by_css_selector(css_menu_items)
    click_and_wait(driver, elements[i])
    log("Navigation complete")
    active_elements = driver.find_elements_by_css_selector(css_menu_active_font)
    active_texts = [ element.text for element in active_elements ]
    log("Active item: " + " / ".join(active_texts))

def is_first_item(driver):
    """
    Returns whether the current page of the questionnaire is the first page. It does so by checking if the 
    first item of the menu is the active one. This check is done via the font used: Font12 is the font
    used for the active menu item

    driver: webdriver instance

    returns: True if the current page is the first page of the questionnaire; False otherwise
    """
    element = driver.find_element_by_css_selector(css_menu_items)
    attr = element.get_attribute("class")
    return active_font_classname in attr

if __name__ == "__main__":

    args = parse_arguments()
    
    config_filename = "config-" + args.config + ".py"
#    with open(config_filename, "r") as f:
#        config = json.load(f)

    log_init(args.output_filename)
    exec(open(config_filename).read())

    log("Clockbot start")
    log("Traversal method: " + args.traversal_method)

    creds = read_credentials(args.cred_filename)

    for cred in creds:
        for count in range(args.n_runs):
            driver = startup(args.browser)
            navigate_page(driver, base_url)
            login(driver, cred["Gebruikersnaam"], cred["Wachtwoord"])
            if not is_first_item(driver):
                # We want to process the questionnaire from the 1st page to the last. However,
                # the system stores the last page visited, so after logging in we may not be on
                # the first page. If this is the case we navigate to the first page and
                # restart the browser, to ensure we start at the first page in a fresh browser
                # environment
                log("Not on first page.")
                navigate_first_menu_item(driver)
                stop(driver)
                driver = startup(args.browser)
                navigate_page(driver, base_url)
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
