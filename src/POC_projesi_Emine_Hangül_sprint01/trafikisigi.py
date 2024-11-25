import time
from gpiozero import LED
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

green = LED(5)
yellow = LED(13)
red = LED(26)

try:
    while True:
        #kırmızı açıkken diğerlerini kapalı tutuyoruz.
        red.on()
        yellow.off()
        green.off()
        time.sleep(10)
        #sarı açıkken diğerlerini kapalı tutuyoruz.
        red.off()
        yellow.on()
        green.off()
        time.sleep(3)
        #yeşil açıkken diğerlerini kapalı tutuyoruz.
        red.off()
        yellow.off()
        green.on()
        time.sleep(10)

except KeyboardInterrupt:
    print('Program terminating...')
finally:
    GPIO.cleanup()