import socket
import struct
import cv2
import numpy as np

def start_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((ip, port))
        server_socket.listen(5)
        print(f"Sunucu {ip}:{port} üzerinde dinliyor...")

        client_socket, client_address = server_socket.accept()
        with client_socket:
            print(f"{client_address} ile bağlantı kuruldu.")
            cap = cv2.VideoCapture(0)

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                _, jpeg = cv2.imencode('.jpg', frame)
                frame_size = len(jpeg.tobytes())
                client_socket.sendall(struct.pack('<L', frame_size))
                client_socket.sendall(jpeg.tobytes())

            cap.release()
            cv2.destroyAllWindows()

if __name__ == '__main__':
    IP = "10.0.0.169"
    PORT = 8000
    start_server(IP, PORT)