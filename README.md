🚨 Accident Detection & Real-Time Alert System using CCTV

Python | OpenCV | MobileNet-SSD | Telegram Bot | Pygame

This project detects road accidents from CCTV footage in real time using a pre-trained MobileNet-SSD object detection model.
When a collision is detected, the system:

✔ Draws bounding boxes on detected vehicles
✔ Captures the accident frame
✔ Sends an alert to Telegram (with location + image)
✔ Logs the incident into alerts.csv
✔ Plays an audio alarm

This system can be used for traffic monitoring, smart surveillance, and safety automation.

📁 Project Folder Structure
Accident-Detection/
│
├── object_detection.py
├── camera_config.json
├── alert.wav
├── alerts.csv
│
├── models/
│   ├── MobileNetSSD_deploy.caffemodel
│   ├── MobileNetSSD_deploy.prototxt
│
├── static/
│   └── captured_frame.jpg
│
├── sample_video.mp4
├── README.md

🔧 1. Installation
Step 1 — Install Python 3.8+

Download from:
https://www.python.org/downloads/

Step 2 — Install required libraries

Open terminal:
pip install opencv-python numpy pygame requests

📡 2. Create Telegram Bot

1.Open Telegram
2.Search @BotFather
3.Type /newbot → get BOT_TOKEN
4.Create a group or use your own chat
5.Open this URL in browser:
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
6.Copy chat_id
Replace in code:
BOT_TOKEN = "your_token_here"
CHAT_ID = "your_chat_id"

📍 3. Configure Camera Location

Edit camera_config.json:
{
  "cam_1": {
    "name": "CIT Main Gate",
    "lat": 11.0283,
    "lon": 76.9366
  }
}

Update according to your camera.

🎥 4. Run the System
python object_detection.py

The system will:
-Load MobileNet-SSD model
-Detect cars, bikes, persons
-Track overlap of bounding boxes
-Identify sustained collision
-Send Telegram alert
-Save snapshot in static/captured_frame.jpg
-Log information to alerts.csv

⚙️ How It Works (Technical Overview)
1. Object Detection
Uses MobileNet-SSD (Caffe model) to detect:
-car
-motorbike
-person
Bounding boxes are extracted from model output.

2. Collision Detection
The system checks bounding box overlap for multiple frames:
-If two object boxes overlap
-For ≥ 5 consecutive frames
 → Collision confirmed

3. Alerts & Logging
When collision detected:
-Plays alarm using pygame
-Saves snapshot
-Sends photo + GPS link to Telegram
-Writes entry to alerts.csv

📦 Important Files Explained
object_detection.py
Main script handling:
-Video reading
-Object detection
-Overlap calculation
-Alert sending
-Logging

camera_config.json
Stores metadata for each CCTV camera (ID, name, GPS).

alerts.csv
Stores history of detected accidents:
timestamp, status, camera_id, cam_name, lat, lon, snapshot_path

models/
Contains MobileNet-SSD model files.

🧪 Testing With Your Own Video
Replace:
  sample_video.mp4
with any CCTV footage:
  python object_detection.py

  🛠️ Troubleshooting
❌ No bounding boxes shown
  -Wrong model path
  -Video too blurry
  -Detection confidence too high

Try lowering confidence:
  if confidence > 0.3:

❌ Telegram alert not received
-Wrong BOT_TOKEN
-Wrong CHAT_ID
-Internet issue

❌ alert.wav fails to play
Use .wav file only.

❌ No CSV log
Make sure alerts.csv is writable.

📘 Future Enhancements
✔ YOLOv8/YOLOv9 model for better accuracy
✔ Flask dashboard for monitoring
✔ Severity ranking using speed estimation
✔ Live RTSP CCTV stream support
