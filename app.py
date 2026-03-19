from flask import Flask, render_template, Response, jsonify, request
import cv2
import time
import numpy as np
import threading
import os

app = Flask(__name__)

# --- SPATIAL CONFIG ---
MAST_HEIGHT_M = 5.0 # Known reference
ALARM_THRESHOLD_M = 4.3

state = {
    "height_m": 4.8,
    "status": "NOMINAL",
    "fog_mode": False,
    "enhance_mode": False,
    "history": []
}
state_lock = threading.Lock()

# 1. THE "LEXSI LABS" FEATURE: Adverse Weather Robustness
def apply_weather_effects(frame, mode="fog"):
    if mode == "fog":
        fog = np.full(frame.shape, 220, dtype=np.uint8)
        return cv2.addWeighted(frame, 0.5, fog, 0.5, 0)
    return frame

def de_haze(frame):
    """CLAHE Enhancement for Low Visibility"""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    return cv2.cvtColor(cv2.merge((l,a,b)), cv2.COLOR_LAB2BGR)

def frame_generator():
    cap = cv2.VideoCapture("static/sim_bg.mp4")
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret: 
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        frame = cv2.resize(frame, (1280, 720))
        h, w = frame.shape[:2]

        # Apply Fog if enabled
        if state["fog_mode"]: frame = apply_weather_effects(frame)
        # Apply AI Enhancement if enabled
        if state["enhance_mode"]: frame = de_haze(frame)

        # MATH: Sine-wave logic for height
        elapsed = time.time() - start_time
        sim_m = 4.45 + 0.45 * np.sin(elapsed * 0.4) 
        
        # CALIBRATION: Map meters to pixels
        ground_y = int(h * 0.85)
        ppm = (h * 0.5) / MAST_HEIGHT_M
        low_y = int(ground_y - (sim_m * ppm))
        
        # --- HUD OVERLAYS (The "Unique" Look) ---
        # 1. Scanning Grid
        for i in range(0, w, 100): cv2.line(frame, (i, 0), (i, h), (50,50,50), 1)
        # 2. Safety Line
        cv2.line(frame, (0, int(ground_y - 4.3*ppm)), (w, int(ground_y - 4.3*ppm)), (0,0,255), 2)
        # 3. Dynamic Tracking Line
        cv2.line(frame, (0, low_y), (w, low_y), (0, 255, 255), 1)

        # Update State
        with state_lock:
            state["height_m"] = round(sim_m, 2)
            state["status"] = "CRITICAL" if sim_m < ALARM_THRESHOLD_M else "NOMINAL"
            state["history"].append(state["height_m"])
            if len(state["history"]) > 30: state["history"].pop(0)

        # On-Video Text
        color = (0,0,255) if state["status"] == "CRITICAL" else (0,255,0)
        cv2.putText(frame, f"SENS_01: {state['status']}", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        if state["enhance_mode"]:
            cv2.putText(frame, "AI_ENHANCEMENT: ACTIVE", (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

        ret, buf = cv2.imencode(".jpg", frame)
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
        time.sleep(0.04)

@app.route("/")
def index(): return render_template("index.html")

@app.route("/video_feed")
def video_feed(): return Response(frame_generator(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/status")
def status(): return jsonify(state)

@app.route("/toggle", methods=["POST"])
def toggle():
    feat = request.json.get("feature")
    with state_lock:
        if feat == "fog": state["fog_mode"] = not state["fog_mode"]
        if feat == "enhance": state["enhance_mode"] = not state["enhance_mode"]
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
