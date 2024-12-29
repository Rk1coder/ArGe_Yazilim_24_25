import socket #Ağ üzerinden iletişim kurmak için kullanılır
import struct #Göndereceğimiz veriyi byte halinde paketlemek için kullanılır
import cv2 as cv #Kamera açmak için kullandığımız kütüphane



#Bağlantı sağlanacak kısımm
def stream(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as jetsonSocket: # TCP POjetsonSocket adında socket oluştur ve
        jetsonSocket.bind((ip, port)) #TCP sunucusunu başlat
        jetsonSocket.listen(5) #maksimum bağlanabilecek istemci sayısı
        print("Waiting for connection...")
        connection, address = jetsonSocket.accept() #istemcinin bağlantı isteğinin kabul et
        print("Connection address:", address) #İstemcinin adresi
        with connection.makefile("wb") as file: #Verileri yazmak için write binart formatında dosya nesnesi oluşturulur
            openCamera(file)  # Kamera işlemi burada çağrılır.


def openCamera(file):
    cap = cv.VideoCapture(0)#kamerayı başlatır
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)#kameranın width değerini değiştir
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)#kameranın height değerini değiştir
    cap.set(cv.CAP_PROP_FPS, 24)#fps değerini ayarla


    while True:#her frameyi tek tek oku
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting ...")
            break


        #her frameyi JPEG formatında sıkıştırır
        _, jpeg = cv.imencode(".jpeg", frame)

        if not _:
            print("Failed to convert image to jpeg. Exiting ...")
            break


        data = jpeg.tobytes() #jpeg dosyasını byte formatına dönüştürür

        file.write(struct.pack('<L', len(data))) #Görüntü verisinin uzunluğu 4 baytlık bir formatta paketlenir ve gönderilir. Bu, alıcı tarafa gelen verinin boyutunu anlamasını sağlar.
        file.write(data)#Sıkıştırılmış görüntü verisi gönderilir.
        file.flush()#Buffer'daki veri hemen gönderilir.



    cap.release()

if __name__ == "__main__":

    IP = "10.0.0.169"#jetson ip adresi
    PORT = 8000 # 3000 ve 65000 arasında rastgele bir port belirlenebilir
    stream(IP, PORT)