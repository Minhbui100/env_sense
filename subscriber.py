import paho.mqtt.client as mqtt
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="environment",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

def on_message(client, userdata, msg):
    device = msg.topic.split("/")[-1]
    temp, hum = msg.payload.decode().split(",")

    cur.execute(
        "insert into sensor_data (device, temperature, humidity) values (%s,%s,%s)",
        (device, temp, hum)
    )
    conn.commit()

    print(device, temp, hum)

client = mqtt.Client()
client.connect("localhost")

client.subscribe("sensors/#")
client.on_message = on_message

print("Listening for ESP32 data...")
client.loop_forever()