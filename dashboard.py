import streamlit as st
import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO
import tempfile
import numpy as np
from PIL import Image
import requests

# === Configuration ===
MODEL_PATH = 'D:/Yolo_v11_model/runs/detect/train2/weights/best.pt'
SAVE_PATH = './Fire_and_Smoke_Detections'
LABELS = ['fire', 'smoke']
CONFIDENCE_THRESHOLD = 0.4

# Telegram Configuration
TELEGRAM_BOT_TOKEN = '7553714157:AAHebs0DXb7nI4a1xQxKHjDXEJLVMacBXqU'
TELEGRAM_CHAT_ID = '1120555837'

# === Model Loading ===
model = YOLO(MODEL_PATH)

# === Utility Functions ===
def clean_path(path):
    return path.strip().strip('"')

def send_telegram_alert(image_path, label_name, threat_level):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"🚨 Alert: {label_name.upper()} detected!\nThreat Level: {threat_level}\nTime: {timestamp}"
    files = {'photo': open(image_path, 'rb')}
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": message}
    response = requests.post(url, data=data, files=files)
    if response.status_code == 200:
        print(f"[INFO] Alert sent successfully: {message}")
    else:
        print(f"[ERROR] Failed to send alert. Status Code: {response.status_code}")


def save_and_alert(frame, label_name, threat_level):
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    image_path = os.path.join(SAVE_PATH, f"{label_name}_{timestamp}.jpg")
    cv2.imwrite(image_path, frame)
    send_telegram_alert(image_path, label_name, threat_level)


# === Detection Logic ===
def detect_and_display(frame):
    results = model(frame)[0]
    detections = results.boxes
    for box in detections:
        conf = float(box.conf[0])
        label = int(box.cls[0])
        label_name = model.names[label]
        if label_name in LABELS and conf >= CONFIDENCE_THRESHOLD:
            frame = results.plot()
            x1, y1, x2, y2 = box.xyxy[0]
            area = (x2 - x1) * (y2 - y1)
            threat_level = 'High' if area > 50000 else 'Medium' if area > 20000 else 'Low'
            save_and_alert(frame, label_name, threat_level)
    return frame


# === Streamlit Interface ===
st.title("🔥 Fire & Smoke Detection Dashboard")

option = st.radio("Choose input type:", ["📁 Upload Video/Image", "🎥 Live Webcam Detection"])

# === Control Buttons ===
start_detection = st.button("Start Detection")
stop_detection = st.button("Stop Detection")


if option == "📁 Upload Video/Image":
    uploaded_file = st.file_uploader("Drag and drop a video or image file", type=["mp4", "avi", "jpg", "jpeg", "png"])
    if uploaded_file and start_detection:
        if uploaded_file.type.startswith("video"):
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())
            cap = cv2.VideoCapture(tfile.name)
            st.success("🔍 Detection started. Press 'Stop Detection' to quit.")
            cv2.namedWindow('Video Detection', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Video Detection', 800, 600)
            while cap.isOpened() and not stop_detection:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = detect_and_display(frame)
                cv2.imshow('Video Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()


elif option == "🎥 Live Webcam Detection":
    if start_detection:
        cap = cv2.VideoCapture(0)
        st.success("🔍 Webcam Detection started. Press 'Stop Detection' to quit.")
        cv2.namedWindow('Webcam Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Webcam Detection', 800, 600)
        while cap.isOpened() and not stop_detection:
            ret, frame = cap.read()
            if not ret:
                break
            frame = detect_and_display(frame)
            cv2.imshow('Webcam Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

