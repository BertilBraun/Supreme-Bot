from joblib import Parallel, delayed
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import config
import time
import os

# chapta
# buy stats - count when getting to compleated page
# only buy certain amount

go_on = True
products_bought = {}

def timeme(method):
    def wrapper(*args, **kw):
        startTime = time.time()
        result = method(*args, **kw)
        if method.__name__ == "Order" and result:
            print(method.__name__, (int(round(time.time() * 1000)) - int(round(startTime * 1000))) / 1000, 's', *args)
        return result
    return wrapper

@timeme
def get(driver, url, check=lambda d : True):
    for _ in range(config.retries):
        driver.get(url)
        if driver.current_url == url and check(driver):
            break
        if "429" in driver.title:
            time.sleep(config.timeout_at_too_many_requests)
        else:
            time.sleep(config.normal_timeout)
    else:
        return False
    return True

@timeme
def add_to_cart(driver, url):
    try:
        # add to cart
        driver.find_element_by_xpath('//*[@id="add-remove-buttons"]/input').click()        
        time.sleep(.1)
    except:
        try:
            driver.find_element_by_xpath('//*[@id="add-remove-buttons"]/b')
        except:
            get(driver, url)
            raise Exception("No add to cart button") 
        else:       
            raise Exception("Sold out")

@timeme    
def checkout(driver, name, product):

    @timeme
    def check(driver):
        try: 
            driver.find_element_by_xpath('//*[@id="order_billing_name"]') 
        except: 
            return False
        else:
            return True

    if not get(driver, 'https://www.supremenewyork.com/checkout', check):
        raise Exception("Cant get checkout Page to load")
    
    elements = [
        #select Germany
        driver.find_element_by_xpath('//*[@id="order_billing_country"]'),
        
        #select mastercard and expriration date
        driver.find_element_by_xpath('//*[@id="credit_card_type"]'),
        driver.find_element_by_xpath('//*[@id="credit_card_month"]'),
        driver.find_element_by_xpath('//*[@id="credit_card_year"]'),
    ]
    
    values = [
        config.keys['country'],

        config.keys['card_type'],
        config.keys['exp_month'],
        config.keys['exp_year']
    ]

    driver.execute_script("""for (i = 0; i < arguments[0]; i++)
                                arguments[1][i].selectedIndex = arguments[2][i] - 1;""",
                               len(elements), elements, values)
    
    elements = [
        driver.find_element_by_xpath('//*[@id="order_billing_name"]'),
        driver.find_element_by_xpath('//*[@id="order_email"]'),
        driver.find_element_by_xpath('//*[@id="order_tel"]'),
        driver.find_element_by_xpath('//*[@id="bo"]'),
        driver.find_element_by_xpath('//*[@id="order_billing_city"]'),
        driver.find_element_by_xpath('//*[@id="order_billing_zip"]'),

        driver.find_element_by_xpath('//*[@id="cnb"]'),
        driver.find_element_by_xpath('//*[@id="vval"]')
    ]
    
    values = [
        config.keys['name'],
        config.keys['email'],
        config.keys['phone'],
        config.keys['address'],
        config.keys['city'],
        config.keys['zip'],
    
        config.keys['card_number'],
        config.keys['card_cvv']
    ]

    driver.execute_script("""for (i = 0; i < arguments[0]; i++)
                                arguments[1][i].value = arguments[2][i];""",
                               len(elements), elements, values)
    
    driver.find_element_by_xpath('//*[@id="cart-cc"]/fieldset/p/label/div/ins').click()
    
    time.sleep(config.checkout_delay)
    if products_bought.get(name, 0) < product.amount:
        driver.find_element_by_xpath('//*[@id="pay"]/input').click()
        driver.maximize_window()
        return True
    else:
        driver.close()
        return False
 
@timeme
def order(url, name, product):
    # load chrome
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #options.add_argument('user-data-dir=www.supremenewyork.com')
    options.add_experimental_option("detach", True)
	
    driver = webdriver.Chrome(options=options)
    driver.minimize_window()
    
    @timeme
    def Order():
        try:
            add_to_cart(driver, url)        
        except Exception as e:
            raise Exception("Add to Cart Error", e.args)
        try:
            return checkout(driver, name, product)     
        except Exception as e:
            raise Exception("Checkout Error", e.args)
        
    if not get(driver, url):
        print("Cant load product page")
        return False

    while True:
        try:
            res = Order()
        except Exception as e:
            print("Failed to Order:", name, e.args)
            if ("Sold out",) in e.args:
                driver.close()
                return False
            time.sleep(config.normal_timeout)
        else:
            global products_bought
            if res:
                products_bought[name] = products_bought.get(name, 0) + 1
            return True

@timeme
def process_link(link):
    
    link = 'https://www.supremenewyork.com' + link
    
    content = str(requests.get(link).content)
    start = content.index("<h1") + 1
    start = content.index("<h1", start) + 1
    start = content.index(">", start) + 1
    end = content.index("<", start)
    name = content[start:end]
    
    @timeme
    def check_product(product):
        if not product.type in link:
            return
        # if link contains type
        if any(key in name for key in product.keywords):
            # if any keywords match - can be changed to all if only exact prducts should be bought
            while go_on and products_bought.get(name, 0) < product.amount:
                if not order(link, name, product):
                    break

    Parallel(n_jobs=len(config.products), backend="threading")(map(delayed(check_product), config.products))
        

# scrape all articles every x seconds
# when new ones arrive request every item page to check the name on seperate threads
# if name contains keywords add to cart and initiate checkout

if __name__ == '__main__':
    
    path = 'links.dat'
    if not os.path.exists(path):
        open(path, 'w').close()

    while go_on:
        URL = 'https://www.supremenewyork.com/shop/new'
        soup = BeautifulSoup(requests.get(URL).content, 'html.parser')

        links = [article.find('div').find('a')['href'] for article in soup.find_all('article')]
    
        with open(path, 'r+') as f:
            if (f.read() not in ("", str(links))) or config.dev:
                f.write(str(links))

                Parallel(n_jobs=16, backend="threading")(map(delayed(process_link), links))
                break

        time.sleep(0.25)

    print(products_bought)

else:
    order('https://www.supremenewyork.com/shop/jackets/eq90f43yk/gks2fnre5', 'Jacket', config.products[0])
    
    
    
# reCAPTCHA driver.find_element_by_xpath("//iframe[contains(@src,'https://www.google.com/recaptcha/api2/anchor')]")