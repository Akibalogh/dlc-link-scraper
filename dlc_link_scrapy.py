from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse, urljoin
import os
import time

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless to avoid UI pop-up
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_internal_links(driver, domain):
    try:
        # Explicitly wait for all 'a' elements to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
        )
    except TimeoutException:
        print("Timed out waiting for page to load. Proceeding with available content.")
        time.sleep(5)

    all_links = driver.find_elements(By.TAG_NAME, 'a')
    internal_links = set()
    for link in all_links:
        href = link.get_attribute('href')
        if href:
            full_url = urljoin('https://' + domain, href)  # Ensure full URL
            if urlparse(full_url).netloc.endswith(domain):
                internal_links.add(full_url)
    return internal_links

def clean_url(url):
    clean = urlparse(url).netloc + urlparse(url).path
    clean = clean.replace('/', '_').replace('?', '_').replace('&', '_').strip('_')
    return clean[:200]  # Limit filename length

def scrape_site(driver, start_url, domain, subfolder):
    visited_urls = set()
    urls_to_visit = {start_url}
    
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
    
    while urls_to_visit:
        url = urls_to_visit.pop()
        if url in visited_urls:
            continue
        visited_urls.add(url)
        
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        body_content = driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML')
        filename = f"{subfolder}/{clean_url(url)}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(body_content)
        
        print(f"Saved: {filename}")
        
        internal_links = get_internal_links(driver, domain)
        urls_to_visit.update(internal_links - visited_urls)

if __name__ == '__main__':
    start_url = 'https://dlc.link'
    domain = 'dlc.link'
    
    driver = initialize_driver()
    try:
        scrape_site(driver, start_url, domain, 'downloaded_pages')
    finally:
        driver.quit()
