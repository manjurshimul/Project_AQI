import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime

def scrape_aqi_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    url = "https://www.iqair.com/world-air-quality-ranking"
    
    try:
        driver.get(url)
        time.sleep(5) 

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Using the broader table find since class names can be long/dynamic
        table = soup.find('table') 
        
        rows = []
        for tr in table.find_all('tr')[1:]: 
            cols = tr.find_all('td')
            if len(cols) >= 3:
                # Target the <a> tag you found in inspect element
                location_element = cols[1].find('a')
                if location_element:
                    full_location = location_element.text.strip() # "Kolkata, India"
                    
                    if "," in full_location:
                        # Split by the last comma to handle cases like "Washington, D.C., USA"
                        parts = full_location.rsplit(',', 1)
                        city = parts[0].strip()
                        country = parts[1].strip()
                    else:
                        city = full_location
                        country = "Unknown"
                else:
                    city, country = "Unknown", "Unknown"

                rows.append({
                    'rank': cols[0].text.strip(),
                    'city': city,
                    'country': country,
                    'aqi_value': int(cols[2].text.strip()),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return pd.DataFrame(rows)

    finally:
        driver.quit()

if __name__ == "__main__":
    df = scrape_aqi_data()
    
    # Adding the Pollution Category for Tableau
    def get_category(v):
        if v <= 50: return "Good"
        if v <= 100: return "Moderate"
        if v <= 150: return "Unhealthy for Sensitive Groups"
        if v <= 200: return "Unhealthy"
        if v <= 300: return "Very Unhealthy"
        return "Hazardous"
    
    df['aqi_category'] = df['aqi_value'].apply(get_category)
    
    print(df.head())
    df.to_csv("aqi_data_final.csv", index=False)