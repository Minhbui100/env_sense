import serial
import psycopg2

ser = serial.Serial('COM4', 115200, timeout=10)

conn = psycopg2.connect(
    host="localhost",
    database="environment",
    user="postgres",
    password="Dynamic@00"
)
cur = conn.cursor()

while True:
    line = ser.readline().decode(errors="ignore").strip()

    try:
        temp, hum = line.split(",")
        temp=round(float(temp))
        hum=round(float(hum))

        cur.execute(
            "insert into dht11 (temperature, humidity) values (%s, %s)",
            (temp, hum)
        )
        conn.commit()

        print("Saved:", temp, hum)

    except Exception as e:
        print("error:", line, e)