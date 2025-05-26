import os
import shutil
import random
import string
import json
import time
import pyautogui
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options


# === CONFIG ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOZILLA_PROFILES_PATH = os.path.join(BASE_DIR, "profiles")
FIREFOX_PATH = r"C:\Program Files\Mozilla Firefox\firefox.exe"
GECKODRIVER_PATH = os.path.join(BASE_DIR, "geckodriver.exe")
FOXYPROXY_XPI_PATH = os.path.join(BASE_DIR, "utils", "foxyproxy@eric.h.jung.xpi")


# === UTILS ===
def check_if_profile_exists(profile_name):
    try:
        with open(os.path.join(BASE_DIR, "profiles.json")) as f:
            data = json.load(f)
        return profile_name in data
    except:
        return False

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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
                "hostname": ip,
                "port": port,
                "username": username,
                "password": password,
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
    with open(os.path.join(BASE_DIR, "utils", "proxy.json"), "w") as f:
        json.dump(proxy, f, indent=4)

def get_extension_uuid(profile_name):
    profile_path = os.path.join(MOZILLA_PROFILES_PATH, profile_name, "storage", "default")
    for filename in os.listdir(profile_path):
        if "moz-extension" in filename:
            return filename.split("+")[3].split("^")[0]
    raise Exception("Extension UUID not found")

# === CORE FUNCTION ===
def configure_proxy_extension(profile_name, proxy_ip, proxy_port, proxy_username, proxy_password):
    # Ensure Firefox is installed
    if not os.path.exists(FIREFOX_PATH):
        raise FileNotFoundError(f"Firefox binary not found at: {FIREFOX_PATH}")

    # Configure Firefox options
    options = Options()
    options.binary_location = FIREFOX_PATH
    profile_path = os.path.join(MOZILLA_PROFILES_PATH, profile_name)
    options.add_argument("-profile")
    options.add_argument(profile_path)
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("marionette.enabled", False)

    # Start browser
    service = FirefoxService(executable_path=GECKODRIVER_PATH)
    browser = webdriver.Firefox(service=service, options=options)

    # Spoof detection
    browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Install proxy extension
    browser.install_addon(FOXYPROXY_XPI_PATH, temporary=False)
    extension_uuid = get_extension_uuid(profile_name)
    browser.get(f"moz-extension://{extension_uuid}/content/options.html")
    time.sleep(2)

    try:
        browser.switch_to.alert.dismiss()
    except:
        pass

    # Load proxy JSON
    generate_proxy_profile(proxy_ip, proxy_port, proxy_username, proxy_password)
    json_import_input = browser.find_element(By.XPATH, '//div[@class="buttons"]/label[@data-i18n="import"]/input')
    json_import_input.send_keys(os.path.join(BASE_DIR, "utils", "proxy.json"))
    browser.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(1)
    browser.find_element(By.XPATH, '/html/body/article/section[3]/fieldset/button[1]').click()
    time.sleep(1)

    # Activate proxy via shortcut
    browser.switch_to.window(browser.window_handles[-1])
    time.sleep(1)
    browser.find_element(By.XPATH, '/html/body/div/div[2]/div/addon-shortcuts/div[2]/div[2]/input').send_keys(Keys.ALT, "a")
    browser.switch_to.window(browser.window_handles[0])
    time.sleep(1)
    pyautogui.hotkey("alt", "a")
    time.sleep(1)

    # Save profile config
    try:
        with open(os.path.join(BASE_DIR, "profiles.json")) as f:
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

    with open(os.path.join(BASE_DIR, "profiles.json"), "w") as f:
        json.dump(profile_data, f, indent=4)

    # Check IP
    browser.get("https://api.myip.com/")
    time.sleep(3)
    print("Public IP:", browser.find_element(By.TAG_NAME, "body").text)
    browser.quit()

# === ENTRY POINT ===
if __name__ == "__main__":
    input_path = os.path.join(BASE_DIR, "input.csv")
    source_profile_path = os.path.join(BASE_DIR, "utils", "base_profile")

    with open(input_path, "r", newline="") as f:
        reader = csv.reader(f)
        input_data = list(reader)

    for row in input_data:
        print("Input row:", row)
        email = row[0].strip()
        profile_name = email.split("@")[0]

        proxy_full = row[4].strip()
        proxy_auth = proxy_full.split("@")[0]
        proxy_host = proxy_full.split("@")[1].split(":")[0]
        proxy_port = proxy_full.split("@")[1].split(":")[1]
        proxy_username = proxy_auth.split(":")[0]
        proxy_password = proxy_auth.split(":")[1]

        destination_path = os.path.join(MOZILLA_PROFILES_PATH, profile_name)
        if check_if_profile_exists(profile_name):
            print(f"Profile {profile_name} already exists. Skipping.")
            continue

        if os.path.exists(destination_path):
            shutil.rmtree(destination_path)

        shutil.copytree(source_profile_path, destination_path)
        print(f"✅ Created profile at: {destination_path}")

        configure_proxy_extension(profile_name, proxy_host, proxy_port, proxy_username, proxy_password)
