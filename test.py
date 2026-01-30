from machine import Pin
from utime import sleep_ms

pins=[15,2,0,4,5,18,19,21,22,23]

while True: 
    for i in range(10):
        led=Pin(pins[i], Pin.OUT)
        led.value(1)
        led1=Pin(pins[10-1-i], Pin.OUT)
        led1.value(1)
        sleep_ms(100)
        led.value(0)
        led1.value(0)
        

