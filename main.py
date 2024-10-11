#!/usr/bin/python3
import time
import json
from daftlistings import Daft, Location, SearchType, PropertyType
import requests
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

def apply(daft_link, user_data):
    print(user_data)
    try:
        # Initialize the ChromeDriver with the appropriate service and options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        #options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = chrome_options)
        #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        # Open a webpage
        driver.get(daft_link)
        # Locate the text input field and fill it out
        # maximizing browser
        driver.maximize_window() 
        time.sleep(4)
        #driver.findElement(By.id("didomi-notice-agree-buttont")).click();
        try:
            if driver.find_element(By.XPATH, "//button[@id='didomi-notice-agree-button']").size() != 0:
                driver.find_element(By.XPATH, "//button[@id='didomi-notice-agree-button']").click()
                time.sleep(2)
        except Exception as e:
            pass

        #login form
        driver.find_element(By.XPATH, "//a[@data-testid='top-level-active-nav-link']").click()
        time.sleep(3)
        driver.find_element(By.XPATH, '//input[@id="username"]').send_keys( user_data['login'] )
        driver.find_element(By.XPATH, '//input[@id="password"]').send_keys( user_data['pass'] )
        time.sleep(2)
        driver.find_element(By.XPATH, '//input[@id="login"]').click()
        time.sleep(2)
        #####
        driver.find_element(By.XPATH, "//button[@data-testid='message-btn']").click()
        time.sleep(10)

        #Filling form
        driver.find_element(By.XPATH, '//input[@id="keyword1"]').send_keys( user_data['first_name'] )
        driver.find_element(By.XPATH, '//input[@id="keyword2"]').send_keys( user_data['last_name'] )
        driver.find_element(By.XPATH, '//input[@id="keyword3"]').send_keys( user_data['email'] )
        driver.find_element(By.XPATH, '//input[@id="keyword4"]').send_keys( user_data['phone'] )


        driver.find_element(By.XPATH, "//button[@data-testid='adultTenants-increment-button']").click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[@data-testid='adultTenants-increment-button']").click()
        time.sleep(1)


        # Enter Application text
        driver.find_element(By.XPATH, '//textarea[@id="message"]').send_keys( user_data['message'] )
        time.sleep(3)
        #driver.find_element(By.XPATH, '//*[@id="contact-form-modal"]/div[2]/form/div/div[5]/div/button').click()
        time.sleep(2)
        #driver.find_element(By.XPATH, '//*[@id="contact-form-modal"]/div[1]/button').click()
        # Close the WebDriver
        driver.quit()

    except Exception as e:
        return f"Error with application to { daft_link } : {e} "
    else:
        return "Applied to  " + daft_link




def search():
    # Open and read the JSON file
    with open('.daft-env', 'r') as file:
        try:
            data = json.load(file)
        except Exception as e:
            print("Error while openining config", e)

    TOKEN = data["bot_token"]
    chat_ids = str(data["chat_ids"])
    chat_ids = chat_ids.split(',')
    # Print the data
    #print("Current settings for searching:")
    #print(data, len(data['daft_details']))

    # Getting previous links
    saved_listings = []
    with open("listings.txt",'r+') as f:
        #f.seek(0)
        for line in f.readlines():
            line_parts = line.strip().split("/")
            listing_id = line_parts[-1]
            if len(listing_id) > 0:
                saved_listings.append(int(listing_id))
        #print(saved_listings)


    i=1
    for item in data['daft_details']:
        print('Setting:', i)
        i=i+1
        for k, v in item.items():
            print(k,v)
        
        #Searching results for this setting
        try:
            daft = Daft()
            location_attribute = getattr(Location, item['location'])
            daft.set_location(location_attribute)
            daft.set_search_type(SearchType.RESIDENTIAL_RENT)
            daft.set_min_beds(int(item['min_beds']))
            daft.set_max_price(int(item['max_price']))
            listings = daft.search()

            new_links = []

            #Filtering search result
            for listing in listings:
                listing_dict = listing.as_dict()
                if listing_dict['id'] in saved_listings:
                    continue
                #if 'numBathrooms' in listing_dict:
                #    print(listing_dict['numBathrooms'])
                link = 'https://www.daft.ie' + listing_dict['seoFriendlyPath']
                print(link)
                if link not in new_links:
                    new_links.append(link)
                    #Sending telegram message
                    message = listing_dict['title'] + '\n' + listing_dict['price'] + ' ' + listing_dict['numBedrooms'] + '\n' + link
                    if data['user_data']['apply'] and int(data['user_data']['num_beds_to_apply']) == int(item['min_beds']):
                        print("Trying to apply")
                        #Trying to send application to the found property
                        result = apply(link, data['user_data'])
                        print(result)
                        message = message + '\n' + result
                    for chat_id in chat_ids:
                        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
                        print(requests.get(url).json()) # this sends the message


            with open("listings.txt",'a') as f:
                for line in new_links:
                    f.write(f"{line}\n")
        except Exception as e:
            #Sending telegram message
            message = f"Error happened with searching \n {e}" 
            for chat_id in chat_ids:
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
                print(requests.get(url).json()) 



#search()
schedule.every(1).minutes.do(search) 
  
while True: 
    schedule.run_pending() 
    time.sleep(1) 
