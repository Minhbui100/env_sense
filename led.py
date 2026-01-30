from machine import Pin
from utime import sleep_ms

led = Pin(25, Pin.OUT)
led.value(0)

while True:
    led.value(1)
    sleep_ms(1000)
    led.value(0)
    sleep_ms(1000)