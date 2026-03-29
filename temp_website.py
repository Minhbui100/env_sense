from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import psycopg2
import time


conn = psycopg2.connect(
    host="localhost",
    database="environment",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

URL = "https://www.accuweather.com/en/us/richmond/77469/hourly-weather-forecast/335868"

def get_weather():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(URL)

        # Wait until a temperature element appears
        temp_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'°')]")
            )
        )

        temperature = temp_element.text

        # Find humidity text
        humidity_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'Humidity')]")
            )
        )

        humidity = humidity_element.text.split()
        

        temperature = float(temperature.replace("°F", ""))
        humidity[1] = float(humidity[1].replace("%", ""))

        cur.execute("""
            INSERT INTO outside_data (temperature, humidity)
            VALUES (%s, %s)
        """, (temperature, humidity[1]))

        conn.commit()


    except Exception as e:
        print("Error getting weather data:", e)

    finally:
        driver.quit()


while True:
    time.sleep(5*60) 
    get_weather()         
        
