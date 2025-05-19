import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO
from tqdm import tqdm

# Custom modules
from utils import speak_alert, log_detection, estimate_threat
from config import MODEL_PATH, SAVE_PATH, CONFIDENCE_THRESHOLD, ALERT_COOLDOWN_SECONDS, LOG_CSV_PATH, LABELS

def clean_path(path):
    return path.strip().strip('"')

def run_detection(input_type='file', input_path=None):
    print("[INFO] Loading model...")
    model = YOLO(MODEL_PATH)
    print("[INFO] Model loaded.")

    is_webcam = (input_type == 'webcam')

    if is_webcam:
        cap = cv2.VideoCapture(0)
        alert_message = "⚠️ Fire near the laptop!"
        source_name = "Webcam"
        delay = 1
        total_frames = None
        progress_bar = None
    else:
        input_path = clean_path(input_path)
        cap = cv2.VideoCapture(input_path)
        alert_message = "Fire or Smoke detected!"
        source_name = os.path.basename(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = max(1, int(1000 / fps))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        progress_bar = tqdm(total=total_frames, desc="Processing Video")

    if not cap.isOpened():
        print("[ERROR] Unable to open video source.")
        return

    print(f"[INFO] Starting detection on: {source_name}")

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_name = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    video_path = os.path.join(SAVE_PATH, video_name)
    out = cv2.VideoWriter(video_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

    last_alert_time = 0

    cv2.namedWindow('Detection', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Detection', 800, 600)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        start_time = time.time()
        results = model(frame)[0]

        for box in results.boxes:
            conf = float(box.conf[0])
            label = int(box.cls[0])
            if conf >= CONFIDENCE_THRESHOLD:
                label_name = model.names[label]
                if label_name in LABELS:
                    frame = results.plot()
                    x1, y1, x2, y2 = box.xyxy[0]
                    threat_level = estimate_threat(x2 - x1, y2 - y1)
                    if time.time() - last_alert_time > ALERT_COOLDOWN_SECONDS:
                        speak_alert(f"{label_name.upper()} detected - Threat Level: {threat_level}")
                        log_detection(label_name, conf, threat_level, "Detected", log_file=LOG_CSV_PATH)
                        out.write(frame)
                        last_alert_time = time.time()

        end_time = time.time()
        adjusted_delay = max(1, int((end_time - start_time) * 1000))

        cv2.imshow('Detection', frame)
        if cv2.waitKey(adjusted_delay) & 0xFF == ord('q'):
            break

        if progress_bar:
            progress_bar.update(1)

    cap.release()
    if out:
        out.release()
    if progress_bar:
        progress_bar.close()
    cv2.destroyAllWindows()
    print(f"[INFO] Detection ended. Video saved to {video_path}")
