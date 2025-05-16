import os
import shutil
import sys
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver import ActionChains
import pyautogui
import json



MOZILLA_PROFILES_PATH = "./profiles"
SCRIPT_PATH = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(SCRIPT_PATH)

def check_if_profile_exists(profile_name):
    try:
        with open(f"{BASE_DIR}/profiles.json") as f:
            data = json.load(f)
    except:
        return False
    try:
        data[profile_name]
        return True
    except KeyError:
        return False


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_proxy_profile(ip, port, username, password):
    proxy = {
        "mode": f"{ip}:{port}",
        "sync": False,
        "autoBackup": False,
        "passthrough": "",
        "theme": "",
        "container": {},
        "commands": {
            "setProxy": f"{ip}:{port}",
            "setTabProxy": "",
            "includeHost": "",
            "excludeHost": ""
        },
        "data": [
            {
            "active": True,
            "title": f"{ip}:{port}",
            "type": "socks5",
            "hostname": f"{ip}",
            "port": f"{port}",
            "username": f"{username}",
            "password": f"{password}",
            "cc": "US",
            "city": "Florida",
            "color": "#a52a2a",
            "pac": "",
            "pacString": "",
            "proxyDNS": True,
            "include": [],
            "exclude": [],
            "tabProxy": []
            }
        ]
    }
    with open(f"{BASE_DIR}/utils/proxy.json", "w") as f:
        json.dump(proxy, f, indent=4)

def get_extension_uuid(profile_name):
    profile_path = os.path.join(MOZILLA_PROFILES_PATH, profile_name)
    print(profile_path)
    extensions_data_path = profile_path + "/storage/default/"
    print(extensions_data_path)
    for filename in os.listdir(extensions_data_path):
        if "moz-extension" in filename:
            extension_path = os.path.join(extensions_data_path, filename)
            break
    extension_uuid = extension_path.split("+")[3].split("^")[0]
    return extension_uuid

def configure_proxy_extension(profile_name, proxy_ip, proxy_port, proxy_username, proxy_password):
    options = webdriver.FirefoxOptions()
    print
    # Set the path to the Chrome driver.
    options.add_argument("-profile")
    options.add_argument(f"./profiles/{profile_name}")
    options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0")
    options.set_preference('dom.webdriver', False)
    options.set_preference('enable-automation', False)
    options.set_preference('dom.webdriver.enabled', False)
    options.set_preference('useAutomationExtension', False)
    options.set_preference('devtools.jsonview.enabled', False)
    options.set_preference('marionette.enabled', False)
    options.set_preference('fission.bfcacheInParent', False)
    options.set_preference('focusmanfocusmanager.testmode', False)
    options.set_preference('fission.webContentIsolationStrategy', 0)


    service = webdriver.FirefoxService( executable_path='./geckodriver' )
    browser = webdriver.Firefox(service=service,  options=options)
    browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    browser.install_addon("./utils/foxyproxy@eric.h.jung.xpi", temporary=False)
    extension_uuid = get_extension_uuid(profile_name)
    browser.get(f"moz-extension://{extension_uuid}/content/options.html")
    time.sleep(2)
    try:
        browser.switch_to.alert.dismiss()
    except:
        print('No alert present')
    

    generate_proxy_profile(proxy_ip, proxy_port, proxy_username, proxy_password)

    time.sleep(1)
    json_import_input = browser.find_element(By.XPATH, '//div[@class="buttons"]/label[@data-i18n="import"]/input')
    json_import_input.send_keys(f"{BASE_DIR}/utils/proxy.json")
    browser.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(1)
    browser.find_element(By.XPATH, '/html/body/article/section[3]/fieldset/button[1]').click()
    time.sleep(1)
    browser.switch_to.window(browser.window_handles[-1])
    time.sleep(1)
    browser.find_element(By.XPATH, '/html/body/div/div[2]/div/addon-shortcuts/div[2]/div[2]/input').send_keys(Keys.ALT, "a")
    browser.switch_to.window(browser.window_handles[0])
    time.sleep(1)
    browser.find_element(By.XPATH, '//html').send_keys(Keys.ALT, "a")
    pyautogui.hotkey("alt", "a")
    time.sleep(1)

    try:
        with open(f"{BASE_DIR}/profiles.json") as f:
            profile_data = json.load(f)
    except:
        profile_data = {}
    profile_data[profile_name] = {
        "profile_name": profile_name,
        "proxy_ip": proxy_ip,
        "proxy_port": proxy_port,
        "proxy_username": proxy_username,
        "proxy_password": proxy_password
    }
    with open(f"{BASE_DIR}/profiles.json", "w") as f:
        json.dump(profile_data, f, indent=4)

    # Navigate to a service that returns the public IP to confirm the proxy configuration
    browser.get("https://api.myip.com/")
    time.sleep(3)
    public_ip = browser.find_element(By.TAG_NAME, "body").text
    print(f"Public IP: {public_ip}")
    browser.quit()
    
if __name__ == "__main__":
    # Load the input CSV file
    input_data = []

    with open(f"{BASE_DIR}/input.csv", "r", newline="") as f:
        for row in f:
            input_data.append(row.split(","))
    
    for row in input_data:
        print((row))
        profile_name = row[0].split("@")[0]
        proxy_ip = row[4].split("@")[1].split(":")[0]
        proxy_port = row[4].split("@")[1].split(":")[1]
        proxy_username = row[4].split("@")[0].split(":")[0]
        proxy_password = row[4].split("@")[0].split(":")[1]
        source_profile_path = "./utils/base_profile"
        destination_path = os.path.join(MOZILLA_PROFILES_PATH, profile_name)
        if check_if_profile_exists(profile_name):
            print(f"Profile {profile_name} already exists.")
            continue


        if os.path.exists(destination_path):
            shutil.rmtree(destination_path)
        shutil.copytree(source_profile_path, destination_path)
        print(f"Profile created to {destination_path}")
        configure_proxy_extension(profile_name, proxy_ip, proxy_port, proxy_username, proxy_password)

    