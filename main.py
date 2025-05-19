import tkinter as tk
from tkinter import filedialog
from detect import run_detection

def upload_file():
    file_path = filedialog.askopenfilename(
        title="Select Video/Image File",
        filetypes=[("Video/Image Files", "*.mp4 *.avi *.mov *.jpg *.jpeg *.png")]
    )
    if file_path:
        print(f"[INFO] Selected file: {file_path}")
        run_detection(input_type="file", input_path=file_path)

def start_webcam():
    print("[INFO] Starting webcam detection...")
    run_detection(input_type="webcam")

def main():
    root = tk.Tk()
    root.title("🔥 Fire & Smoke Detection System 🔥")
    root.geometry("420x220")
    root.resizable(False, False)

    label = tk.Label(root, text="Choose Input Type", font=("Arial", 16, "bold"))
    label.pack(pady=20)

    upload_button = tk.Button(root, text="📹 Upload Video/Image", command=upload_file, width=30, height=2, bg="#f0f0f0")
    upload_button.pack(pady=10)

    webcam_button = tk.Button(root, text="🎥 Start Live Webcam Detection", command=start_webcam, width=30, height=2, bg="#f0f0f0")
    webcam_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()