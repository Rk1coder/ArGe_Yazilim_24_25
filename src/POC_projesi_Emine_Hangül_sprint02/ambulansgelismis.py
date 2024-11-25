import cv2 #görüntü işleme kütüphanesidir.
import RPi.GPIO as GPIO
from gpiozero import LED, Buzzer

min_width=20
min_height=10

mavi=LED(17)
buzzer=Buzzer(10)

GPIO.setmode(GPIO.BCM)

car_cascade=cv2.CascadeClassifier(cv2.data.haarcascades+ 'haarcascade_car.xml') #car_cascade araçları algılamak için sınıflandırmadır.

cap=cv2.VideoCapture(0) #kameradan görüntü alıyoruz raspberry pi için 0

try:
    while True:
        ret, frame = cap.read() #ret görüntü alma başarılıysa true değilse false döner.
        if not ret:
            print("can't get camera image!")
            break

        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #görüntüleri gri tonlamalara çevirir.

        cars=car_cascade.detectMultiScale(gray, 1.1, 3)

        vehicle_detected = False
        for (x, y, w, h) in cars:
            if w>=min_width and h>=min_height:
                vehicle_detected = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if vehicle_detected:
            print("vehicle found!")
            mavi.on()
            buzzer.on()
        else:
            mavi.off()
            buzzer.off()

        if cv2.waitKey(1) & 0xFF == ord('.'): #.kullanıldığında programdan çıkılacak.
            break
finally:
    mavi.off()
    buzzer.off()
    GPIO.cleanup()
    cap.release()
    cv2.destroyAllWindows()
