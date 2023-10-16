from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import os
import re
import time
from pprint import pprint
import pandas as pd
from bs4 import BeautifulSoup

# Set Chrome options for Selenium
options = Options()
options.add_argument("--headless=new")  # Run Chrome in headless mode
options.add_argument("user-agent=Chrome/80.0.3987.132")  # Set user-agent
options.add_argument("--window-size=1920,1080")  # Set window size

# Create a ChromeDriver instance with ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Set the URL of the website
url = 'https://www.homes.com/homes-for-sale/?sk=bKQGNiTZM-2TOnjzdIpHc9r8fvsOljeHkDTek1zs6TM&bb=-2vih3-xpOzh2n_tiO'

# Function to make an HTTP request to the given URL and return the parsed HTML using BeautifulSoup
def listResponse(url):
    driver.get(url)
    time.sleep(0.2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup

# Initial HTTP request to get the total number of pages
soup = listResponse(url)

# Extract the number of pages from the website
num_pages = int(soup.find('span', class_="pageRange").contents[0].split('of')[1].strip())

# Base URL for the property listing pages
base_url = "https://www.homes.com/homes-for-sale/p"
page_links = []

# Generate links for all pages
for page_number in range(1, num_pages + 1):
    url = f'{base_url}{page_number}/?sk=bKQGNiTZM-2TOnjzdIpHc9r8fvsOljeHkDTek1zs6TM&bb=-2vih3-xpOzh2n_tiO'
    page_links.append(url)

# Initialize lists and data frame for storing data
listings_url = []
listings_url = list(set(listings_url))  # Remove duplicates
df_list = []

# Iterate through the page links and scrape data
for link in page_links:
    soup = listResponse(link)
    house_listings = soup.find_all('div', {"class": "for-sale-content-container"})

    for i in range(len(house_listings)):
        for j in range(len(listings_url)):
            href = house_listings[i].find('a').get('href')
            property_url = "https://www.homes.com" + href
            listings_url.append(property_url)

            price = house_listings[i].find('p', class_='price-container').contents[0].strip()
            listings_url.append(property_url)
            listings_url = list(set(listings_url))  # Remove duplicates

            inner_soup = listResponse(listings_url[j])

            full_name = inner_soup.find("a", class_="agent-information agent-information-fullname standard-link text-only").contents[0].strip()
            first_name = full_name.split(" ")[0]
            last_name = full_name.split(" ")[1]
            address = inner_soup.find("title").contents[0].split('-')[0]
            city = address.split(', ')[1]

            phone_number = inner_soup.find("a", class_="agent-information agent-information-phone-number standard-link text-only").contents[0]
            email = inner_soup.find('span', class_="agent-information agent-information-email").contents[0]

            info_dict = {"First Name": first_name,
                         "Last Name": last_name,
                         "Full Name": full_name,
                         "Phone Number": phone_number,
                         "Email Address": email,
                         "Listing Price": price,
                         "Listing Address": address,
                         "City": city,
                         "Link": property_url}
            df_list.append(info_dict)

# Create a Pandas DataFrame from the collected data
df = pd.DataFrame(df_list)

# Save the DataFrame to a CSV file
df.to_csv("real_estate_listings_CA.csv", index=False)
