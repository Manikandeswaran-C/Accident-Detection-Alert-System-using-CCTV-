import cv2
import numpy as np
import pygame
import requests
import time
import csv
import json
from datetime import datetime

# ========== CAMERA CONFIG ==========
CAMERA_ID = "cam_1"  # ID of current CCTV
with open("camera_config.json", "r") as f:
    CAMCFG = json.load(f)

CAM_NAME = CAMCFG[CAMERA_ID]["name"]
CAM_LAT  = CAMCFG[CAMERA_ID]["lat"]
CAM_LON  = CAMCFG[CAMERA_ID]["lon"]

def maps_link(lat, lon):
    return f"https://maps.google.com/?q={lat},{lon}"

# ========== ALERT SOUND ==========
pygame.mixer.init()
try:
    alert_sound = pygame.mixer.Sound("alert.wav")
    print("✅ alert.wav loaded")
except Exception as e:
    print(f"❌ Failed to load alert.wav: {e}")

alert_playing = False

# ========== MODEL ==========
net = cv2.dnn.readNetFromCaffe(
    'models/MobileNetSSD_deploy.prototxt',
    'models/MobileNetSSD_deploy.caffemodel'
)

cap = cv2.VideoCapture("sample_video.mp4")
if not cap.isOpened():
    print("❌ Error opening video.")
    exit()

# ========== TELEGRAM ALERT SETUP ==========
last_alert_time = 0
alert_cooldown = 60  # seconds
BOT_TOKEN ='7880610521:AAFI26aaKToUfqUURjFwx8piI9uS56TlEQU'
CHAT_ID ='6157478609'
# ========== ALERT LOGGING ==========
def log_alert(snapshot_path):
    with open("alerts.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Collision Detected",
            CAMERA_ID,
            CAM_NAME,
            CAM_LAT,
            CAM_LON,
            snapshot_path
        ])

# ========== SEND TELEGRAM PHOTO ALERT ==========
def send_telegram_alert_with_photo(image_path):
    caption = (
        f"🚨 Collision Detected!\n"
        f"📍 {CAM_NAME}\n"
        f"🗺️ Location: {CAM_LAT}, {CAM_LON}\n"
        f"🔗 {maps_link(CAM_LAT, CAM_LON)}"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(image_path, 'rb') as photo:
            res = requests.post(
                url, 
                data={'chat_id': CHAT_ID, 'caption': caption}, 
                files={'photo': photo}
            )
        print("📨 Telegram image alert sent:", res.status_code)
    except Exception as e:
        print(f"❌ Telegram photo error: {e}")

# ========== CLASS LABELS ==========
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
           "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike",
           "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

# ========== HELPER FUNCTION ==========
def get_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) // 2, (y1 + y2) // 2)

# ========== TRACKING / COLLISION ==========
persistent_overlap_counter = 0
overlap_threshold = 5

# ========== MAIN LOOP ==========
while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    boxes = []
    centers = []
    labels = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            idx = int(detections[0, 0, i, 1])
            label = CLASSES[idx]
            if label in ["car", "motorbike", "person"]:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                box = box.astype("int")
                boxes.append(box)
                centers.append(get_center(box))
                labels.append(label)

    # ========== COLLISION DETECTION ==========
    overlap_found = False
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            box1, box2 = boxes[i], boxes[j]
            overlap = not (
                box1[2] < box2[0] or box2[2] < box1[0] or
                box1[3] < box2[1] or box2[3] < box1[1]
            )
            if overlap:
                overlap_found = True
                cv2.rectangle(frame, (box1[0], box1[1]), (box1[2], box1[3]), (0, 0, 255), 3)
                cv2.rectangle(frame, (box2[0], box2[1]), (box2[2], box2[3]), (0, 0, 255), 3)

    if overlap_found:
        persistent_overlap_counter += 1
    else:
        persistent_overlap_counter = 0

    collision_detected = persistent_overlap_counter >= overlap_threshold
    if collision_detected:
        print("⚠️ COLLISION DETECTED!")
        cv2.putText(frame, "🚨 Collision!", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    # ========== DRAW OBJECTS ==========
    for i, box in enumerate(boxes):
        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
        cv2.putText(frame, labels[i], (box[0], box[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # ========== ALERT HANDLING ==========
    now = time.time()
    if collision_detected:
        if not alert_playing:
            print("🔊 Playing alert sound...")
            try:
                alert_sound.play()
                time.sleep(2)
                alert_playing = True
            except Exception as e:
                print(f"❌ Sound error: {e}")
        if now - last_alert_time > alert_cooldown:
            snapshot_path = "static/captured_frame.jpg"
            cv2.imwrite(snapshot_path, frame)
            send_telegram_alert_with_photo(snapshot_path)
            log_alert(snapshot_path)
            last_alert_time = now
    else:
        if alert_playing:
            print("🛑 Stopping sound.")
            alert_sound.stop()
            alert_playing = False

    # ========== SHOW VIDEO ==========
    cv2.imshow("Accident Detection System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ========== CLEAN UP ==========
cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
