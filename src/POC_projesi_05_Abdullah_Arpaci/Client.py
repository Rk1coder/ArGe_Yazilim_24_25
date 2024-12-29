import socket #Ağ üzerinden iletişim kurmak için kullanılır
import struct #Veri alışverişinde byte halinde paketlemek için kullanılır
import numpy as np
import cv2 #Kamera açmak için kullandığımız kütüphane
from ultralytics import YOLO #Nesne takibi için kullandığımız kütüphane



model = YOLO("yolov8n.pt") #Nesne takibi için kullanacağımız model


def connect(ip,port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
        clientSocket.connect((ip,port)) #  İstemci, belirtilen IP ve port adresinde sunucuya bağlanır.
        data_buffer = b'' #veri alma sürecinde kullanılan bir tampon oluşturuluyor.
        while True:

            while len(data_buffer) < 4:#Sunucudan gelen ilk 4 bayt, görüntü çerçevesinin (frame) boyutunu belirtir.
                data_buffer += clientSocket.recv(4)#4 baytlık veri alır ve tamponu günceller.
            frame_size = struct.unpack('<L', data_buffer[:4])[0]#Küçük-endian formatında (<L) 4 baytlık bir tamsayıyı çözümleyerek çerçeve boyutunu elde eder.
            data_buffer = data_buffer[4:] # İşlenmiş boyut bilgisini tampondan çıkarır.


            while len(data_buffer) < frame_size:
                data_buffer += clientSocket.recv(frame_size - len(data_buffer))#Bu döngü, belirtilen frame_size kadar veriyi alıncaya kadar tamponu doldurur.
            jpeg = data_buffer[:frame_size] #Alınan çerçeve verisi.
            data_buffer = data_buffer[frame_size:] #İşlenmiş çerçeve verisini tampondan çıkarır.

            frame = cv2.imdecode(np.frombuffer(jpeg, dtype=np.uint8), cv2.IMREAD_COLOR) #JPEG formatındaki veriyi çözerek NumPy dizisine dönüştürür ve OpenCV tarafından okunabilir bir format olan cv2.IMREAD_COLOR modunda görüntüyü alır.
            objectDetection(frame)
            cv2.imshow("Received Video", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

#Yolo ile nesne takibi
def objectDetection(frame):
    results = model.predict(frame, verbose=False)


    for box in results[0].boxes:

        x_center, y_center, w, h = box.xywh[0].tolist()
        confidence = box.conf[0].item()
        class_id = int(box.cls[0].item())

        if confidence > 0.5:
            x_center = int(x_center)
            y_center = int(y_center)
            w = int(w)
            h = int(h)

            x1 = x_center - w // 2
            y1 = y_center - h // 2
            x2 = x_center + w // 2
            y2 = y_center + h // 2

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Class: {class_id}, Conf: {confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


if __name__ == '__main__':
    IP = "10.0.0.169" #bağlanılacak İp adresi
    PORT = 8000 #bağlanılacak port bilgisi
    connect(IP,PORT)