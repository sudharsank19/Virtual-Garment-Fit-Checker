from flask import Flask, render_template, Response, request, jsonify
import cv2
from collections import deque

from app.camera_stream import get_camera, read_frame
from app.body_detection import estimate_body_measurements
from app.fit_checker import check_fit
from app.utils import load_json
from app.garment_overlay import overlay_garment

app = Flask(__name__)
cap = get_camera()

garments = load_json('data/garment_measurements.json')
manual_user = load_json('data/user_measurements.json')

selected_garment = "shirt_m"
mode = "manual"

latest_fit = {}
latest_user_meas = {}

# Smoothing config
measurement_buffer = deque(maxlen=10)
frame_counter = 0

@app.route('/')
def index():
    return render_template(
        "index.html",
        garments=list(garments.keys()),
        selected=selected_garment,
        mode=mode,
        user_meas=latest_user_meas,
        fit=latest_fit
    )

@app.route('/update_settings', methods=["POST"])
def update_settings():
    global selected_garment, mode
    selected_garment = request.json.get('garment')
    mode = request.json.get('mode')
    return jsonify(status="updated")

def generate_frames():
    global latest_fit, latest_user_meas, frame_counter

    while True:
        frame = read_frame(cap)
        if frame is None:
            break

        if mode == "auto":
            frame_counter += 1
            detection = estimate_body_measurements(frame)
            if detection:
                measurement_buffer.append(detection)

            if frame_counter % 10 == 0 and measurement_buffer:
                averaged = {}
                for key in measurement_buffer[0]:
                    averaged[key] = sum(m[key] for m in measurement_buffer) / len(measurement_buffer)
                latest_user_meas = {k: round(v, 2) for k, v in averaged.items()}
                latest_fit = check_fit(latest_user_meas, garments[selected_garment])
        else:
            latest_user_meas = manual_user
            latest_fit = check_fit(latest_user_meas, garments[selected_garment])

        garment_img_path = f'static/garments/{selected_garment}.png'
        frame = overlay_garment(frame, garment_img_path)

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
