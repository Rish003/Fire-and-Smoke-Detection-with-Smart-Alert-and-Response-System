# utils.py
import pyttsx3
import cv2
import os
import pandas as pd
from datetime import datetime  # ✅ Only this is needed

# Text-to-speech alert
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak_alert(message):
    print("[ALERT]", message)
    engine.say(message)
    engine.runAndWait()

# Save alert frame
def save_frame(frame, save_path):
    """Save the frame as an image to the given path."""
    os.makedirs(save_path, exist_ok=True)
    filename = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    path = os.path.join(save_path, filename)
    cv2.imwrite(path, frame)
    print(f"[INFO] Frame saved to {path}")

# Estimate threat level based on size
def estimate_threat(width, height):
    area = width * height
    if area >= 50000:
        return "High"
    elif area >= 20000:
        return "Medium"
    else:
        return "Low"

# Log detection to CSV
def log_detection(label, confidence, threat, context, log_file):
    log_entry = {
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Label': label,
        'Confidence': round(confidence, 2),
        'Threat Level': threat,
        'Context': context
    }
    df = pd.DataFrame([log_entry])
    if not os.path.exists(log_file):
        df.to_csv(log_file, index=False)
    else:
        df.to_csv(log_file, mode='a', header=False, index=False)



