from machine import Pin
from utime import sleep
import dht 

led = Pin(25, Pin.OUT)
sensor = dht.DHT11(Pin(14))

while True:
  try:
    sleep(2)
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    temp_f = temp * (9/5) + 32.0
    print('Temperature: %3.1f C' %temp)
    print('Temperature: %3.1f F' %temp_f)
    print('Humidity: %3.1f %%' %hum)

    if temp_f>78:
      led.value(1)
    else:
      led.value(0)
  except OSError as e:
    print('Failed to read sensor.')
