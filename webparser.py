from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from twilio.rest import Client
import time
import json
import os
from dotenv import load_dotenv


load_dotenv()

purchase = {}

def extract_walmart_price(driver, url):
    driver.get(url)
    cost = driver.find_element(By.XPATH, r'//*[@id="main-buybox"]/div[1]/div[4]/div/div[1]/div/div/div/span/span').text

    return cost

def extract_amazon_price(driver, url):

    driver.get(url)
    cost = driver.find_element(By.CLASS_NAME, "a-price-whole").text + "." + driver.find_element(By.CLASS_NAME, "a-price-fraction").text

    return cost

def notification(cost, name, platform):
    account_sid = os.environ["ACCOUNT_SID"]
    auth_token = os.environ["AUTH_TOKEN"]
    twilio_num = os.environ["TWILIO_NUM"]
    receiver = os.environ["RECIEVER"]
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                              body=f""" Hey Good News! {name} has dropped to {cost} on {platform}!
                              \nGo Get It Now or reply to this text with "BUY" to automatically purchase it!
                              """,
                              from_=twilio_num,
                              to=receiver
    )

def writeJSON(productRecords, name="productRecords.json"):
    # Serializing json
    json_object = json.dumps(productRecords, indent=4)
    
    # Writing to sample.json
    with open(name, "w") as outfile:
        outfile.write(json_object)

def main():
    """This function will accept the search term and the maximum price you are
    expecting the product to be"""

    # startup the webdriver

    while True  :

        try:
            
            with open('productRecords.json') as db:
                productRecords = json.load(db)

        except:
            continue

        if productRecords:
            driver = webdriver.Chrome(r"C:\Users\bsun7\OneDrive\Documents\chromedriver\chromedriver.exe")
            for link in productRecords.keys():
                platform = productRecords[link]["platform"]
                price = productRecords[link]["price"]
                name = productRecords[link]["name"]
                
                if platform == "Amazon":
                    cost = extract_amazon_price(driver, link)
                    if float(cost) <= float(price):
                        notification(cost, name, platform)
                        purchase[name] = link
                        productRecords.pop(link)
                        writeJSON(productRecords)
                        writeJSON(purchase, "purchases.json")
                        break

            time.sleep(10)
            driver.close()
        time.sleep(2)




if __name__ == '__main__':
    main()