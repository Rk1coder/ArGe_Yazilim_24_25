from gpiozero import MotionSensor, Buzzer
from time import sleep

pirSensor = MotionSensor(22)
buzzer = Buzzer(27)

while True:
    pirSensor.wait_for_motion()
    buzzer.on()
    print("Hareket var")
    sleep(1)
    pirSensor.wait_for_no_motion()
    print("Hareket yok")
    buzzer.off()
    sleep(1) 
