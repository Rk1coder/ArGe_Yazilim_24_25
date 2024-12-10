from pymavlink import mavutil
import pandas as pd
import matplotlib.pyplot as plt

# Veri dosyasının yolu
log_file_path = "kalp.bin"

# Verilerin tutulacağı yapı
data = {
    "Time (minutes)": [],
    "Roll (degrees)": [],
    "Pitch (degrees)": [],
    "Yaw (degrees)": [],
    "Latitude": [],
    "Longitude": []
}

# Verileri okuma ve işleme
def read_flight_data(log_file_path):
    mavlog = mavutil.mavlink_connection(log_file_path)
    while True:
        message = mavlog.recv_match(blocking=False)
        if message is None:
            break
        if message.get_type() == "GPS":
            gps_data = message.to_dict()
            data["Latitude"].append(gps_data.get("Lat", 0) / 1e7)
            data["Longitude"].append(gps_data.get("Lng", 0) / 1e7)
        elif message.get_type() == "ATT":
            att_data = message.to_dict()
            data["Time (minutes)"].append(att_data.get("TimeUS", 0) / 1e6 / 60)
            data["Roll (degrees)"].append(att_data.get("Roll", 0))
            data["Pitch (degrees)"].append(att_data.get("Pitch", 0))
            data["Yaw (degrees)"].append(att_data.get("Yaw", 0))

# Verileri görselleştirme
def visualize_data(data):
    plt.figure(figsize=(10, 6))
    plt.plot(data["Longitude"], data["Latitude"], marker="o", label="Uçuş Rotası", color="blue")
    plt.xlabel("Boylam")
    plt.ylabel("Enlem")
    plt.title("Uçuş Rotası (Koordinatlar)")
    plt.grid()
    plt.legend()
    plt.show()

    plt.figure(figsize=(12, 8))
    plt.plot(data["Time (minutes)"], data["Roll (degrees)"], label="Roll", color="blue")
    plt.plot(data["Time (minutes)"], data["Pitch (degrees)"], label="Pitch", color="green")
    plt.plot(data["Time (minutes)"], data["Yaw (degrees)"], label="Yaw", color="red")
    plt.xlabel("Zaman (dakika)")
    plt.ylabel("Açı (derece)")
    plt.title("Roll, Pitch ve Yaw Açılarının Zamana Göre Değişimi")
    plt.legend()
    plt.grid()
    plt.show()

# Eksik verileri doldurma
def fill_missing_data(data):
    max_len = max(len(data["Time (minutes)"]), len(data["Latitude"]))
    for key in data:
        while len(data[key]) < max_len:
            data[key].append(None)

# Main işlemleri
read_flight_data(log_file_path)
fill_missing_data(data)

# Verileri DataFrame'e dönüştürme
df = pd.DataFrame(data)

# Terminale waypoint bilgilerini gösterme
print("Waypoint Bilgileri (İlk 10 Satır):")
print(df[["Time (minutes)", "Latitude", "Longitude"]].head(10))

#json formatina dönüştürme
df.to_json("flight_data.json", orient="records", indent=4)

# Verileri görselleştirme
visualize_data(data)
