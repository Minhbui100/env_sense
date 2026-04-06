import time
import requests
import psycopg2
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

LAT = 29.5819
LON = -95.7608
INTERVAL = 5 * 60 

URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    "&current=temperature_2m,relative_humidity_2m"
    "&temperature_unit=fahrenheit"
    "&timezone=America%2FChicago"
)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_weather():
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
        current = resp.json()["current"]
        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            DELETE FROM outside_data WHERE recorded_at < NOW() - INTERVAL '7 days';
            INSERT INTO outside_data (temperature, humidity) VALUES (%s, %s);
            """,
            (temperature, humidity)
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"Outside: {temperature}°F  {humidity}%")

    except Exception as e:
        print("Error fetching weather:", e)

if __name__ == "__main__":
    while True:
        get_weather()
        time.sleep(INTERVAL)
