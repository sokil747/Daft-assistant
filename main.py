#!/usr/bin/python3
import time
import json
from daftlistings import Daft, Location, SearchType, PropertyType
from pprint import pprint
import requests
import schedule


def search():
    # Open and read the JSON file
    with open('.env', 'r') as file:
        data = json.load(file)

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
            saved_listings.append(int(line_parts[-1]))
        print(saved_listings)


    i=1
    for item in data['daft_details']:
        print('Setting:', i)
        i=i+1
        for k, v in item.items():
            print(k,v)
        
        #Searching results for this setting
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
            print("*"*20)
            pprint(listing_dict['title'])
            pprint(listing_dict['price'])
            pprint(listing_dict['numBedrooms'])
            if 'numBathrooms' in listing_dict:
                pprint(listing_dict['numBathrooms'])
            link = 'https://www.daft.ie' + listing_dict['seoFriendlyPath']
            if link not in new_links:
                new_links.append(link)
                pprint(link)
                print("*"*20)
                #Sending telegram message
                message = listing_dict['title'] + '\n' + listing_dict['price'] + ' ' + listing_dict['numBedrooms'] + '\n' + link
                for chat_id in chat_ids:
                    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
                    print(requests.get(url).json()) # this sends the message


        with open("listings.txt",'a') as f:
            for line in new_links:
                f.write(f"{line}\n")

schedule.every(5).minutes.do(search) 
  
while True: 
    schedule.run_pending() 
    time.sleep(1) 

    