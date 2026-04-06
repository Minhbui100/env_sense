import time
import psycopg2
import paho.mqtt.client as mqtt
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, MQTT_BROKER, MQTT_TOPIC

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

conn = None
cur = None

def ensure_db():
    global conn, cur
    try:
        if conn is None or conn.closed:
            conn = get_db_connection()
            cur = conn.cursor()
    except Exception as e:
        print("DB reconnect failed:", e)
        conn = None
        cur = None

def on_connect(client, userdata, _flags, rc):
    if rc == 0:
        print("MQTT connected. Subscribing to", MQTT_TOPIC)
        client.subscribe(MQTT_TOPIC)
    else:
        print("MQTT connection failed, rc =", rc)

def on_message(client, userdata, msg):
    ensure_db()
    if cur is None:
        print("No DB connection, skipping message")
        return
    try:
        device = msg.topic.split("/")[-1]
        temp, hum = msg.payload.decode().split(",")

        cur.execute(
            """
            DELETE FROM sensor_data WHERE recorded_at < NOW() - INTERVAL '7 days';
            INSERT INTO sensor_data (device, temperature, humidity) VALUES (%s, %s, %s);
            """,
            (device, float(temp), float(hum))
        )
        conn.commit()
        print(f"[{device}] temp={temp}  hum={hum}")

    except Exception as e:
        print("Error processing message:", e)
        try:
            conn.rollback()
        except Exception:
            pass

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected MQTT disconnect, will auto-reconnect...")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
ensure_db()

while True:
    try:
        client.connect(MQTT_BROKER)
        client.loop_forever()
    except Exception as e:
        print("MQTT error, retrying in 5s:", e)
        time.sleep(5)
