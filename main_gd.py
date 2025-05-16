from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from selenium.webdriver.common.keys import Keys
from seleniumbase import Driver
import os
import time
import random
import json
import requests
import sys
import socks
import socket
import csv

VEHICLE_MAKES = [
    "acura", "alfa romeo", "aston martin", "audi", "bentley", "bmw", "buick", "cadillac", 
    "chevrolet", "chrysler", "citroën", "dodge", "ferrari", "fiat", "ford", "genesis", 
    "gmc", "honda", "hyundai", "infiniti", "jaguar", "jeep", "kia", "lamborghini", 
    "land rover", "lexus", "lincoln", "maserati", "mazda", "mclaren", "mercedes-benz", 
    "mini", "mitsubishi", "nissan", "peugeot", "porsche", "ram", "renault", "rolls-royce", 
    "saab", "subaru", "suzuki", "tesla", "toyota", "volkswagen", "volvo",
    "aprilia", "arctic cat", "can-am", "ducati", "harley-davidson", "honda motorcycles", 
    "indian", "kawasaki", "ktm", "polaris", "royal enfield", "suzuki motorcycles", 
    "triumph", "vespa", "yamaha", "freightliner", "hino", "international", "kenworth", 
    "mack", "peterbilt", "volvo trucks", "western star", "freightliner", "isuzu"
]

PRODUCT_TITLE_XPATH = '//div[@class="xyamay9 x1pi30zi x18d9i69 x1swvt13"]'
PRODUCT_PRICE_XPATH = '//div[@class="x1xmf6yo"]'
PRODUCT_DESCRIPTION_XPATH = '//div[@class="xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a"]'
PRODUCT_IMAGE_XPATH = "//img[contains(@alt, 'Product photo of')]"

MILEAGE = "background-position: -21px -63px;"
FUEL_TYPE_AND_TRANSMISSION = "background-position: -42px -63px;"
INTERIOR_EXTERIOR_COLOR = "background-position: -84px -21px;"
CONSUMPTION = "background-position: -84px -63px;"
DEBT = "background-position: -84px -63px;"
TITLE = "background-position: -84px -105px;"

abs_path = os.path.abspath(__file__)
dir_path = os.path.dirname(abs_path)

class fbm_scraper():
    def __init__(self, email, password, city_code, profile, threshold=100, headless=False):
        self.threshold = threshold
        
        
        options = webdriver.FirefoxOptions()
        options.add_argument("-profile")
        options.add_argument(f"{dir_path}/profiles/{profile}")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-blink-features=AutomationControlled')
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
        if headless:
            options.headless = True
        service = webdriver.FirefoxService( executable_path='./geckodriver' )
        print("Almost good")
        self.browser = webdriver.Firefox(service=service, keep_alive=True, options=options)
        print("Good")
        self.browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


        self.checkpoint = [x.replace(".json", "") for x in os.listdir(f"{dir_path}/publications/")]
        self.links = {}

        self.url_to_scrap = f"https://www.facebook.com/marketplace/{city_code}/vehicles?sortBy=creation_time_descend&exact=true"

        if self.log_check() == True:
            print(f"INFO: Profile {profile} not logged, attempting a log in.")
            
            captcha = self.log_in(email, password)
            if captcha:
                print(f"WARNING: Captcha/Notification request detected for profile {profile}. Terminating.")
                sys.exit(0)

    def ip_test(self):
        self.browser.get('https://api.ipify.org/')
        ip_address = self.browser.find_element(By.TAG_NAME, "body").text
        print(ip_address)

    def log_check(self):
        try:
            self.browser.get("https://www.facebook.com/")
            WebDriverWait(self.browser, 8).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@aria-label, 'Password')]")))
            return True
        except:
            return False

    def log_in(self, email, password):
        self.browser.get("https://www.facebook.com/login.php?lwv=200")
        email_input = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@aria-label, 'Email')]")))
        password_input = self.browser.find_element(By.XPATH, "//input[contains(@aria-label, 'Password')]")
        self.browser.save_screenshot("login.png")
        self.human_key_input(email_input, email)
        self.human_key_input(password_input, password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

        try:
            notification_prompt = self.browser.find_element(By.XPATH, "//*[contains(text(), 'Go to your Facebook')]")
            captcha = True
        except:
            captcha = False
        try:
            captcha_prompt = self.browser.find_element(By.XPATH, "//span[contains(text(), 'Enter the characters you see')]")
            captcha = True
        except:
            captcha = False
        return captcha

    def execute_scrap_process(self):
        print(f"INFO: Starting the scrap of {self.url_to_scrap}")
        self.browser.get(self.url_to_scrap)
        self.browser.save_screenshot("start.png")
        self.human_scroll()

    def scrap_links(self):
        elements = self.browser.find_elements(By.XPATH, '//div[@class="x3ct3a4"]')
        for element in elements:
            product_href = element.find_element(By.XPATH, 'a')
            product_id = product_href.get_attribute('href').split("/")[5]
            if product_id in self.checkpoint:
                continue
            self.links[product_id] = product_href.get_attribute('href')

    def human_key_input(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.2390, 0.3573))

    def human_scroll(self):
        total_scroll = 1
        recorded_heights = []
        while True:
            random_pixels = random.randint(600, 1300)
            random_wait = random.uniform(1,2.0)
            total_scroll += random_pixels
            # Scroll down to the bottom of the page to load all items.
            self.browser.execute_script(
                f"window.scrollTo(0, {total_scroll});")
            
            current_height = self.browser.execute_script("return document.body.scrollHeight")
            recorded_heights.append(current_height)
            
            if len(recorded_heights) > 1 and all(recorded_heights[-i] == recorded_heights[-i-1] for i in range(1, min(len(recorded_heights), 5))):
                print(f"INFO: No more items to load, starting the scrap of {len(self.links)} items.")
                break
            if len(self.links) >= self.threshold:
                break
            else:
                try:
                    self.scrap_links()
                except:
                    print("WARNING: No more links found or the page has changed during the scroll process.")
                    return

                time.sleep(random_wait)
    
    def scrap_images(self, publication_id, download_images = False):
        container_element = self.browser.find_element(By.XPATH, '//div[@class="x1ja2u2z x78zum5 xl56j7k xh8yej3"]')
        image_elements = container_element.find_elements(By.XPATH, PRODUCT_IMAGE_XPATH)
        if not os.path.exists(f"{dir_path}/images/{publication_id}"):
            os.makedirs(f"{dir_path}/images/{publication_id}")
    
        image_counts = 0
        image_urls = []
        for image_element in image_elements:
            image_url = image_element.get_attribute("src")
            if "https://scontent" in image_url:
                if image_counts >= 3:
                    break
                
                if download_images:
                    r = requests.get(image_url, stream=True)
                    if r.status_code == 200:
                        with open(f"{dir_path}/images/{publication_id}/{publication_id}_{image_counts}.png", 'wb') as f:
                            for chunk in r:
                                f.write(chunk)

                image_urls.append(image_url)
                image_counts += 1

        return image_urls
                
    
    def scrap_publication_date(self):
        ### !!! WARNING: In testing this element has always been the last one in the list, but this may change.
        try:
            posted = self.browser.find_elements(By.XPATH, "//span[contains(text(), 'ago')]")[-1].text
        except:
            return "N/A"
        #about an hour ago

        if "about" in posted:
            numerical_time = 1
            time_period = posted.split(" ")[2]
        elif len(posted.split(" ")) == 3:
            try:
                numerical_time = int(posted.split(" ")[0])
                time_period = posted.split(" ")[1]
            except:
                numerical_time = 1
                time_period = posted.split(" ")[1]
        else:
            return "N/A"


        if "hour" in time_period:
            multiplier = 3600
        elif "minute" in time_period:
            multiplier = 60
        elif "day" in time_period:
            multiplier = 86400
        elif "week" in time_period:
            multiplier = 604800
        
        try:
            seconds_ago = numerical_time * multiplier
            publication_date = time.time() - seconds_ago
            publication_date = time.strftime("%Y-%m-%d", time.localtime(publication_date))
            return publication_date
        except Exception as e:
            return "N/A"


    def scrap_vehicle_info(self): 
        # Due to the format of the attribute 'style' in //i elements changing constantly, we need to iterate through all of them.
        page_i_elements = self.browser.find_elements(By.XPATH, """//i""")
        vehicle_info = {}
        
        for element in page_i_elements:
            try:
                style_attribute = element.get_attribute("style")
                if MILEAGE in style_attribute:
                    parent_element = element.find_element(By.XPATH, "..")
                    grandparent_element = parent_element.find_element(By.XPATH, "..")
                    grandparent_element = grandparent_element.text.split("\n")[0].replace(" miles", "")
                    grandparent_element = grandparent_element.split("\n")[0].replace(",", "")
                    vehicle_info["mileage"] = int(grandparent_element.split("\n")[0].replace("Driven ", ""))
                
                elif INTERIOR_EXTERIOR_COLOR in style_attribute:
                    parent_element = element.find_element(By.XPATH, "..")
                    grandparent_element = parent_element.find_element(By.XPATH, "..")
                    exterior_color = grandparent_element.text.split("\n")[0].split("·")[0].split(":")[-1]
                    try:
                        interior_color = grandparent_element.text.split("\n")[0].split("·")[1].split(":")[-1]
                    except:
                        interior_color = "N/A"
                    
                    vehicle_info["interior_color"] = interior_color.strip()
                    vehicle_info["exterior_color"] = exterior_color.strip()

                elif FUEL_TYPE_AND_TRANSMISSION in style_attribute:
                    if "transmission" in style_attribute:
                        parent_element = element.find_element(By.XPATH, "..")
                        grandparent_element = parent_element.find_element(By.XPATH, "..")
                        vehicle_info["transmission"] = grandparent_element.text.split("\n")[0].replace(" transmission ", "").strip()
                    else:
                        parent_element = element.find_element(By.XPATH, "..")
                        grandparent_element = parent_element.find_element(By.XPATH, "..")
                        vehicle_info["fuel_type"] = grandparent_element.text.split("\n")[0].replace("Fuel type: ", "")

                elif CONSUMPTION in style_attribute:
                    parent_element = element.find_element(By.XPATH, "..")
                    grandparent_element = parent_element.find_element(By.XPATH, "..")
                    city_consumption = float(grandparent_element.text.split("\n")[0].split("·")[0].replace(" MPG city", "").strip())
                    highway_consumption = float(grandparent_element.text.split("\n")[0].split("·")[1].replace(" MPG highway", "").strip())
                    vehicle_info["consumption"] = {"city": city_consumption, "highway": highway_consumption}
                
                elif DEBT in style_attribute:
                    parent_element = element.find_element(By.XPATH, "..")
                    grandparent_element = parent_element.find_element(By.XPATH, "..")
                    vehicle_info["debt"] = grandparent_element.text.split("\n")[0].strip()
                
                elif TITLE in style_attribute:
                    parent_element = element.find_element(By.XPATH, "..")
                    grandparent_element = parent_element.find_element(By.XPATH, "..")
                    vehicle_info["title"] = grandparent_element.text.split("\n")[0].replace(" title", "").strip()
            except Exception as e:
                #print("Unexpected Error:", e)
                None
        
        return vehicle_info
    
    def scrap_seller_profile(self):
        try:
            profile_element = self.browser.find_element(By.XPATH, "//a[contains(@href, '/marketplace/profile')]")
        except:
            return None, None, None, None, None, None, None, None
        profile_href = profile_element.get_attribute("href")
        profile_id = profile_href.split("/")[5]
        self.browser.execute_script("arguments[0].click();", profile_element)
        time.sleep(2)
        car_makes_checks = 0
        listings = self.browser.find_elements(By.XPATH, "//a[contains(@href, '/?ref=marketplace_profile')]")
        for listing in listings:
            try:
                listing_text = listing.text.lower()
            except:
                break
            listing_words = listing_text.split(" ")
            for word in listing_words:
                if word in VEHICLE_MAKES:
                    car_makes_checks += 1
                    break

        
        if car_makes_checks > 1:
            is_dealership = True
        else:
            is_dealership = False
        

        try:
            lives_in = self.browser.find_element(By.XPATH, "//div[contains(text(), 'Lives in')]").text.replace("Lives in ", "").strip()
        except:
            lives_in = "N/A"

        try:
            joined_facebook_in = int(self.browser.find_element(By.XPATH, "//div[contains(text(), 'Joined Facebook in')]").text.replace("Joined Facebook in", "").strip())
        except:
            joined_facebook_in = "N/A"

        try:
            seller_name = self.browser.find_element(By.XPATH, '//span[@class="x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x14z4hjw x1x48ksl x579bpy xjkpybl x1xlr1w8 xzsf02u x1yc453h"]').text.split("\n")[0]
        except:
            seller_name = "N/A"
            
        try:
            ratings = self.browser.find_element(By.XPATH, "//*[contains(text(), 'Based on')]")
            ratings = int(ratings.text.split(" ")[2])
            rating = self.browser.find_element(By.XPATH, '//div[@class="x3nfvp2"]')
            rating = rating.get_attribute("aria-label")
            rating = float(rating.split(" ")[0])
        except:
            ratings = "N/A"
            rating = "N/A"
        return seller_name, is_dealership, profile_id, lives_in, joined_facebook_in, car_makes_checks, ratings, rating
    
    def scrap_product_location(self):
        location_element = self.browser.find_element(By.XPATH, '//span[@class="x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h"]')
        location_text = location_element.text.split("\n")[0]
        return location_text
    
    def scrap_link(self, link):
        
        self.browser.get(link)
        
        publication_data = {}

        publication_id = link.split("/")[5]
        publication_date = self.scrap_publication_date()
        product_title = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, PRODUCT_TITLE_XPATH))).text.split("\n")[0]
        try:
            product_price = int(self.browser.find_element(By.XPATH, PRODUCT_PRICE_XPATH).text.replace("$", "").replace(",", "").strip())
        except:
            product_price = 0
        try: # Some vehicles may have a short description, no need to click on "See more"
            see_more = self.browser.find_element(By.XPATH, "//*[contains(text(), 'See more')]")
            see_more.click()
        except Exception as e:
            None

        vehicle_info = self.scrap_vehicle_info()
        
        
        try: # Some vehicles may have no description
            publication_description = self.browser.find_element(By.XPATH, PRODUCT_DESCRIPTION_XPATH).text
        except:
            publication_description = "N/A"

        seller_name, is_dealership, profile_id, lives_in_element, joined_facebook_in, car_makes_checks, ratings, rating = self.scrap_seller_profile()
        
        publication_location = self.scrap_product_location()
        image_urls = self.scrap_images(publication_id)
        print(publication_id)


        profile_info = {
            "profile_id": int(profile_id),
            "profile_name": seller_name,
            "is_dealership": is_dealership,
            "lives_in": lives_in_element,
            "joined_facebook_in": joined_facebook_in,
            "car_listings":car_makes_checks,
            "rating": rating,
            "ratings_number": ratings,
            "profile_link": f"https://www.facebook.com/marketplace/profile/{profile_id}/",
            }
        
        publication_info = {
            "publication_id": int(publication_id),
            "publication_date": publication_date,
            "product_title": product_title,
            "product_price": product_price,
            "publication_description": publication_description,
            "publication_link": f"https://www.facebook.com/marketplace/item/{publication_id}/",
            "publication_location": publication_location,
            "images":image_urls
        }
        
        
        data = {
            "date": publication_date,
            "product_title": product_title,
            "product_price": product_price,
            "vehicle_info": vehicle_info,
            "publication_info": publication_info,
            "profile_info": profile_info,
        }

        
        
        return data
    
    def format_files(self):
        pass

if __name__ == "__main__":

    with open(f"{dir_path}/input.csv", "r") as f:
        reader = csv.reader(f)
        lines = list(reader)

    if not os.path.exists(f"{dir_path}/publications"):
        os.makedirs(f"{dir_path}/publications")

    if not os.path.exists(f"{dir_path}/images"):
        os.makedirs(f"{dir_path}/images")


    for line in lines:
        email, password, cities, threshold, proxy = line
        cities = cities.split(";")
        threshold = int(threshold.strip())
        email = email.strip()
        profile = email.split("@")[0]
        for city in cities:
            city = city.replace("[", "").replace("]", "").replace(" ", "")

            if not os.path.exists(f"{dir_path}/publications/{city}"):
                os.makedirs(f"{dir_path}/publications/{city}")

            worker = fbm_scraper(email, password, city, profile, threshold)


            worker.execute_scrap_process()
            for product_id, link in worker.links.items():
                publication = worker.scrap_link(link)    
                with open(f"{dir_path}/publications/{city}/{product_id}.json", "w") as f:
                    json.dump(publication, f, indent=4)
                time.sleep(0.5)
            worker.browser.quit()
