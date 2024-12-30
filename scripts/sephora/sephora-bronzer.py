from curl_cffi import requests
from rich import print
import xmltodict
import csv
import json
from time import sleep
import re
from playwright.sync_api import sync_playwright, TimeoutError
import time

# Script used to scrape for bronzer products from Sephora

class Product:
    def __init__(self, salesPrice, productID, productName, image, targetURL, rating, ingredients, shades):
        self.salesPrice = salesPrice
        self.productID = productID
        self.productName = productName
        self.image = image
        self.targetURL = targetURL
        self.rating = rating
        self.ingredients = ingredients
        self.shades = shades


all_products = []
    
def new_session():
    session = requests.Session(impersonate="chrome")
    return session

def add_delay(seconds):
    sleep(seconds)

def include_product_types(product_name):
    # check if the product name includes the word bronze or bronzer
    included_keywords = r"\b(Bronze|Bronzer)\b"
    return re.search(included_keywords, product_name, re.IGNORECASE)

# scrolling function
def wait_for_button_and_scroll(page, selector, max_retries=10, scroll_step=2000):
    # Scroll manually until the button is visible or max retries are reached
    retries = 0
    while retries < max_retries:
        # Scroll the page
        page.evaluate(f'window.scrollTo(0, window.scrollY + {scroll_step})')
        
        # Wait a little to ensure content loads
        time.sleep(2)
        
        # Check if the button is visible
        if page.is_visible(selector):
            print(f"Button '{selector}' found!")
            return True
        
        retries += 1
    
    print(f"Button '{selector}' not found after {max_retries} retries.")
    return False

# function to close the modal if it appears
def handle_modal(page):
    # Add a delay to wait for pop up or modal to show
    time.sleep(5)
    # Click somewhere in the corner outside of the modal to get out of the modal
    # click three times to make sure
    page.mouse.click(10, 10)
    page.mouse.click(10, 10)
    page.mouse.click(10, 10)

        
# function to scrape details such as ingredients list and shades from targetURL using Playwright
def scrape_product_details(url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
        
            try:
                # Set a longer timeout for initial page load
                page.set_default_timeout(60000)
                page.set_viewport_size({"width": 1280, "height": 800})
                response = page.goto(url)
            
                if response is None or not response.ok:
                    print(f"Failed to load page: {url}")
                    return [], []
            
                # Wait for the main content to load
                page.wait_for_selector('main', timeout=30000)
            
                 # Try to handle modal multiple times
                handle_modal(page)
            
                shade_names = []
                ingredients_names = []
            
                # Get shade colors with retry logic
                try:
                    swatch_selector = 'div[data-comp="SwatchGroup "]'
                    page.wait_for_selector(swatch_selector, timeout=20000)
                    swatch_container = page.query_selector(swatch_selector)
                
                    if swatch_container:
                        shades = swatch_container.query_selector_all('button[aria-label]')
                        shade_names = [shade.get_attribute('aria-label') for shade in shades]
                except Exception as e:
                    print(f"Error getting shades: {e}")
            
                # Scroll handling
                page.evaluate('''() => {
                    window.onscroll = null;
                    document.body.style.overflow = "auto";
                    Object.defineProperty(document.scrollingElement, 'scrollTop', {
                        set: function(val) { this._scrollTop = val; },
                        get: function() { return this._scrollTop || 0; }
                    });
                }''')
            
                # Try to get ingredients
                try:
                    # Click ingredients button if it exists
                    ingredients_button = page.locator('button[data-at="ingredients"]')
                    if ingredients_button.is_visible(timeout=10000):
                        ingredients_button.click()
                    
                        # Wait for ingredients content
                        ingredients_div = page.locator('div#ingredients div.css-1ue8dmw div')
                        if ingredients_div.is_visible(timeout=10000):
                            ingredients_text = ingredients_div.inner_text()
                            ingredients_names = [ingredient.strip() for ingredient in ingredients_text.split(',')]
                except Exception as e:
                    print(f"Error getting ingredients: {e}")
            
            except Exception as e:
                print(f"Error scraping product details: {e}")
            
            finally:
                context.close()
                browser.close()
            
            return ingredients_names, shade_names

    
    
def search_api(session: requests.Session, query: str, start_num: int):
    url = f"https://www.sephora.com/api/v2/catalog/search/?type=keyword&q={query}&content=true&page=60&currentPage={str(start_num)}&loc=en-CA&ch=rwd&countryCode=CA&targetSearchEngine=nlp"
    resp = session.get(url)
    # Delay after sending a request
    add_delay(2)  
    if resp.status_code == 200:
        try:
            #Decode XML
            xml_data = resp.content.decode('utf-8')  
            json_data = xmltodict.parse(xml_data)
            # take each product in the product listing and append it to the products array
            current_product_listing = json_data["KeywordSearchResponse"]["products"]["products"]
            for product in current_product_listing:
                # check if product is actually foundation
                # only add products who have the word bronze or bronzer
                if(include_product_types(product["currentSku"]["imageAltText"])):
                    # then product name is valid 
                    # format target url for product
                    target_url = f"https://www.sephora.com{product["targetUrl"]}"
                    # Get ingredients list and shades list from target url
                    ingredients, shades = scrape_product_details(target_url)
                    # create a product object
                    product_item = Product(product["currentSku"]["listPrice"], product["productId"], product["currentSku"]["imageAltText"], product["heroImage"], target_url, product["rating"], ingredients, shades)
                    # push the product object to the array
                    all_products.append(product_item)
                    # add a 3 second delay
                    add_delay(3)
                
            return len(current_product_listing)
            
        except Exception as e:
            print(f"Error converting XML to JSON: {e}") 
            return 0 
    else:
        print(f"Request failed with status code: {resp.status_code}")
        # return 0 if there's an error
        return 0
    

def get_total_results(session: requests.Session, query: str, start_num: int):
    url = url = f"https://www.sephora.com/api/v2/catalog/search/?type=keyword&q={query}&content=true&page=60&currentPage={str(start_num)}&loc=en-CA&ch=rwd&countryCode=CA&targetSearchEngine=nlp"
    resp = session.get(url)
    if resp.status_code == 200:
        try:
            #Decode XML
            xml_data = resp.content.decode('utf-8')  
            json_data = xmltodict.parse(xml_data) 
            # return results count
            results_count = json_data["KeywordSearchResponse"]["categories"]["categories"][0]["recordCount"]
            return results_count
        except Exception as e:
            print(f"Error converting XML to JSON: {e}") 
    else:
        print(f"Request failed with status code: {resp.status_code}")
        
def get_first_page_results(session: requests.Session, query: str):
    url = url = f"https://www.sephora.com/api/v2/catalog/search/?type=keyword&q={query}&content=true&page=60&currentPage=1&loc=en-CA&ch=rwd&countryCode=CA&targetSearchEngine=nlp"
    resp = session.get(url)
    if resp.status_code == 200:
        try:
            #Decode XML
            xml_data = resp.content.decode('utf-8')  
            json_data = xmltodict.parse(xml_data) 
            # return json data of first page
            return json_data
        except Exception as e:
            print(f"Error converting XML to JSON: {e}") 
    else:
        print(f"Request failed with status code: {resp.status_code}")
        

        
def main():
    session = new_session()
    # Get the total number of results
    PRODUCT_NAME = "bronzer"
    
    total_results = int(get_total_results(session, PRODUCT_NAME, 1))
    # add a deleay of 3 seconds
    add_delay(3)
    # set current index or page to 1
    currIndex = 1
    # Each page has 60 results
    results_scraped = 60
    # loop through pages until number of results scraped reaches total results number
    while results_scraped <= total_results:
        # Call search_api to get products for the current page
        search_results = search_api(session, PRODUCT_NAME, currIndex)

        # Update results_scraped based on the number of products retrieved
        results_scraped += search_results
        
        # add a delay of 5 seconds
        add_delay(5)

        # Increment currIndex to move to the next page
        currIndex += 1
        

    # Mention how many products scraped
    print(f"Scraped {len(all_products)} products in total.")
    
    # Convert Product objects to dictionaries using list comprehension
    product_dicts = [product.__dict__ for product in all_products]
    
    # create a csv file
    with open('sephora_bronzer.csv', 'w', newline='') as csvfile:
        fieldnames = ['salesPrice', 'productID', 'productName', 'image', 'targetURL', 'rating', 'ingredients', 'shades']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(product_dicts)
    

if __name__ == "__main__":
    main()
    
    
        
        
    
    
    
        

    


    