import cv2
import mediapipe as mp
import smtplib
from email.mime.text import MIMEText

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

def eposta_gonder(gonderici_email, sifre, alici_email):
    konu = "Hareket Algılandı!"
    mesaj_metni = "El hareketi algılandı, lütfen kontrol edin."

    mesaj = MIMEText(mesaj_metni)
    mesaj["Subject"] = konu
    mesaj["From"] = gonderici_email
    mesaj["To"] = alici_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as sunucu:
            sunucu.starttls()
            sunucu.login(gonderici_email, sifre)
            sunucu.send_message(mesaj)
            print("E-posta başarıyla gönderildi!")
    except smtplib.SMTPAuthenticationError:
        print("E-posta doğrulama hatası! Lütfen kullanıcı adı ve şifrenizi kontrol edin.")
    except Exception as hata:
        print(f"Beklenmedik bir hata oluştu: {hata}")

GONDERICI_EMAIL = "Gönderici email"
SIFRE = "Şifre"
ALICI_EMAIL = "Alıcı email"

cap = cv2.VideoCapture(0)

hareket_algilandi = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Kamera görüntüsü alınamadı!")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_pip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]

            if index_tip.y > index_pip.y:
                cv2.putText(frame, "Hareket Algilandi!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                if not hareket_algilandi:
                    eposta_gonder(GONDERICI_EMAIL, SIFRE, ALICI_EMAIL)
                    hareket_algilandi = True

            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

