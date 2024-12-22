import socket
import struct
import numpy as np
import cv2

# Yüz tanıma için Haar Cascade modelini yükle
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Yüzlerin ID'lerini takip etmek için bir yapı
tracked_faces = {}

# Yüz takip için ID oluşturma amacıyla kullanılacak sayaç
face_id_counter = 0

def connect_to_server(ip, port):
    """
    Sunucuya bağlanma ve görüntü alma işlemi.
    """
    global tracked_faces, face_id_counter  # Takip edilen yüzler ve ID sayacı global değişkenlerdir.

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((ip, port))  # İstemci, belirtilen IP ve port adresinde sunucuya bağlanır.
        data_buffer = b''  # Veri alma sürecinde kullanılan bir tampon oluşturuluyor.

        while True:
            # Çerçeve boyutunu almak için ilk 4 baytı al
            while len(data_buffer) < 4:
                data_buffer += client_socket.recv(4)

            frame_size = struct.unpack('<L', data_buffer[:4])[0]  # Küçük-endian formatında 4 baytlık bir tamsayıyı çözümleyerek çerçeve boyutunu elde eder.
            data_buffer = data_buffer[4:]  # İşlenmiş boyut bilgisini tampondan çıkarır.

            # Çerçeve boyutuna göre veri al
            while len(data_buffer) < frame_size:
                data_buffer += client_socket.recv(frame_size - len(data_buffer))

            jpeg = data_buffer[:frame_size]  # Alınan çerçeve verisi
            data_buffer = data_buffer[frame_size:]  # İşlenmiş çerçeve verisini tampondan çıkarır.

            # JPEG formatındaki veriyi çözerek NumPy dizisine dönüştürür ve OpenCV tarafından okunabilir bir formatta görüntüyü alır.
            frame = cv2.imdecode(np.frombuffer(jpeg, dtype=np.uint8), cv2.IMREAD_COLOR)
            object_detection(frame)  # Yüz tanımasını gerçekleştir
            cv2.imshow("Received Video", frame)  # Ekranda görüntüyü göster

            # 'q' tuşuna basıldığında döngüden çıkılır
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Ekran kapandığında doğru bir şekilde temizlenir
    cv2.destroyAllWindows()


def object_detection(frame):
    """
    Yüz tanıma ve takip işlemi yapılır. Yüzlere ID atanır ve takip edilir.
    """
    global tracked_faces, face_id_counter  # Takip edilen yüzler ve ID sayacı global değişkenlerdir.

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Renkli görüntüyü gri tonlamaya çevir
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Yüzlerin mevcut koordinatlarını ve ID'lerini saklamak için geçici bir liste oluşturuluyor
    current_faces = []

    for (x, y, w, h) in faces:
        # Yüzün merkez koordinatlarını hesapla
        x_center = x + w // 2
        y_center = y + h // 2

        # Yüzün etrafına dikdörtgen çiz
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Yüzün etiketini hazırlama
        label = "Face"

        # Yüzlerin takip edilmesi
        face_id = None
        for tracked_id, tracked_face in tracked_faces.items():
            # Aynı yüzü bulmak için merkez koordinatları arasındaki farkları kontrol et
            if abs(tracked_face['x_center'] - x_center) < 50 and abs(tracked_face['y_center'] - y_center) < 50:
                face_id = tracked_id
                break

        if face_id is None:
            # Yeni bir yüz, yeni bir ID ataması yapılır
            face_id = face_id_counter
            face_id_counter += 1

        # Takip edilen yüzün verilerini güncelle
        tracked_faces[face_id] = {
            'x': x,
            'y': y,
            'w': w,
            'h': h,
            'x_center': x_center,
            'y_center': y_center
        }

        # Yüzün üzerine ID etiketini ekle
        label = f"ID {face_id}"
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Yüzü geçici listeye ekle
        current_faces.append({'id': face_id, 'x_center': x_center, 'y_center': y_center})

    # Artık gözükmeyen yüzleri takip listesinden çıkar
    for face_id in list(tracked_faces.keys()):
        if face_id not in [face['id'] for face in current_faces]:
            del tracked_faces[face_id]  # Görünmeyen yüzleri listeden sil

if __name__ == '__main__':
    IP = "10.0.0.169"  # Bağlanılacak IP adresi
    PORT = 8000  # Bağlanılacak port bilgisi

    # Sunucuya bağlan ve görüntü al
    connect_to_server(IP, PORT)
