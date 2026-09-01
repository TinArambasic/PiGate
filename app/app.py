from flask import Flask, render_template, request, redirect, jsonify, Response
from database import init_db, add_plate, remove_plate, get_all_plates, get_logs
import cv2
import threading
import sys
sys.path.insert(0, '/home/tin/gate-system')

app = Flask(__name__)
init_db()

latest_frame = None
frame_lock = threading.Lock()

def generate_frames():
    while True:
        try:
            with open('/tmp/pigate_frame.jpg', 'rb') as f:
                frame_bytes = f.read()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except FileNotFoundError:
            time.sleep(0.1)

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/")
def index():
    plates = get_all_plates()
    return render_template("index.html", plates=plates)

@app.route("/logs")
def logs():
    log_entries = get_logs()
    return render_template("logs.html", logs=log_entries)

@app.route("/add_plate", methods=["POST"])
def add_plate_route():
    plate_number = request.form.get("plate_number")
    owner_name = request.form.get("owner_name", "")
    if plate_number:
        add_plate(plate_number, owner_name)
    return redirect("/")

@app.route("/delete_plate/<int:plate_id>", methods=["POST"])
def delete_plate_route(plate_id):
    remove_plate(plate_id)
    return redirect("/")

@app.route("/gate/open", methods=["POST"])
def gate_open():
    try:
        with open('/tmp/gate_command', 'w') as f:
            f.write('open')
        return jsonify({"status": "opening"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/gate/close", methods=["POST"])
def gate_close():
    try:
        with open('/tmp/gate_command', 'w') as f:
            f.write('close')
        return jsonify({"status": "closing"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
