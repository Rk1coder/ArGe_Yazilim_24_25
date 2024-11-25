import RPİ.GPIO as GPIO
import time
from gpiozero import LED,buzzer

count=0
blue= LED(22)
blue2= LED(23)
buzzer=buzzer(6)

frekans=(buzzer,1)
GPIO.setmode(GPIO.BCM)

try:
    while 1:
        blue.off()
        blue2.on()
        buzzer.on()
        time.sleep(1)

        blue.on()
        blue2.off()
        buzzer.on()
        frekans=(buzzer,10)
        time.sleep(5)

        count++
        if count==5:
            break

except KeyboardInterrupt:
    print('program terminating')
finally:
    GPIO.cleanup()