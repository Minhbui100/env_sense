from umqtt.simple import MQTTClient
import network
import dht
from machine import Pin
from utime import sleep

WIFI_SSID = "LeYosemite"
WIFI_PASS = "43Chem#72"

MQTT_BROKER = "10.0.0.7" 
CLIENT_ID = "esp32_room1"
MQTT_TOPIC = "sensors/" + CLIENT_ID

DHT_PIN = 14
SLEEP_INTERVAL = 300

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            sleep(1)
            print("Waiting for Wi-Fi...")
    print("Wi-Fi connected! IP:", wlan.ifconfig()[0])
    return wlan

def connect_mqtt():
    while True:
        try:
            client = MQTTClient(CLIENT_ID, MQTT_BROKER)
            client.connect()
            print("MQTT connected!")
            return client
        except Exception as e:
            print("MQTT connection failed, retrying in 5s...", e)
            sleep(5)

wlan = connect_wifi()
client = connect_mqtt()
sensor = dht.DHT11(Pin(DHT_PIN))

while True:
    try:
        # Reconnect Wi-Fi if lost
        if not wlan.isconnected():
            print("Wi-Fi lost, reconnecting...")
            wlan = connect_wifi()
            client = connect_mqtt()

        # Read sensor
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        msg = "{},{}".format(temp, hum)

        # Publish to MQTT
        client.publish(MQTT_TOPIC, msg)
        print("Sent:", msg)

    except Exception as e:
        print("Error reading sensor or publishing:", e)
        # Try reconnecting MQTT
        client = connect_mqtt()

    sleep(SLEEP_INTERVAL)