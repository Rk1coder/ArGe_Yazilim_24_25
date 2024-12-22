import socket
import struct
import cv2 as cv
import numpy as np

def receive_data(ip, port):
    # YOLO modelini yükle
    net = cv.dnn.readNet("yolov3.weights", "yolov3.cfg")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    # Sınıf etiketlerini yükle
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((ip, port))
        print("Connected to server.")

        while True:
            # Görüntü boyutunu al
            length_data = clientSocket.recv(4)
            if len(length_data) < 4:
                break
            image_length = struct.unpack('<L', length_data)[0]

            # Görüntü verisini al
            image_data = b""
            while len(image_data) < image_length:
                packet = clientSocket.recv(image_length - len(image_data))
                if not packet:
                    break
                image_data += packet

            # Görüntüyü decode et ve göster
            if len(image_data) == image_length:
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv.imdecode(nparr, cv.IMREAD_COLOR)
                if img is not None:
                    # Görüntüyü dnn modeline uygun hale getir
                    blob = cv.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                    net.setInput(blob)
                    outs = net.forward(output_layers)

                    # İnsanları tespit et
                    class_ids = []
                    confidences = []
                    boxes = []
                    height, width, channels = img.shape

                    for out in outs:
                        for detection in out:
                            scores = detection[5:]
                            class_id = np.argmax(scores)
                            confidence = scores[class_id]
                            if confidence > 0.5 and class_id == 0:  # İnsan sınıfı için class_id = 0
                                center_x = int(detection[0] * width)
                                center_y = int(detection[1] * height)
                                w = int(detection[2] * width)
                                h = int(detection[3] * height)

                                # Dikdörtgenin üst sol köşesini hesapla
                                x = int(center_x - w / 2)
                                y = int(center_y - h / 2)

                                boxes.append([x, y, w, h])
                                confidences.append(float(confidence))
                                class_ids.append(class_id)

                    # Non-maxima suppression (NMS) uygulayarak en iyi tespitleri seç
                    indexes = cv.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

                    if len(indexes) > 0:
                        for i in indexes.flatten():
                            x, y, w, h = boxes[i]
                            cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            label = str(classes[class_ids[i]])
                            cv.putText(img, label, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    # Tespit edilen görüntüyü göster
                    cv.imshow("Received Image with People Detection", img)
                    cv.waitKey(1)
                else:
                    print("Failed to decode image.")
            else:
                print("Failed to receive full image data.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        clientSocket.close()

if __name__ == "__main__":
    IP = "10.0.0.169"
    PORT = 7000
    receive_data(IP, PORT)
