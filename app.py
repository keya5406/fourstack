from flask import Flask, render_template, request, jsonify
from services.calibration import (
    save_frame_from_base64,
    start_calibration_from_frame,
    save_coordinates
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("calibration.html")


@app.route("/upload-frame", methods=["POST"])
def upload_frame():

    data = request.json
    frame_data = data.get("frame")

    save_frame_from_base64(frame_data)

    coords = start_calibration_from_frame()

    if coords:
        return jsonify({"status": "ready"})
    else:
        return jsonify({"status": "failed"}), 500


@app.route("/save-coordinates", methods=["POST"])
def save_coordinates_route():

    if save_coordinates():
        return jsonify({"status": "saved"})
    else:
        return jsonify({"status": "no_data"}), 400


if __name__ == "__main__":
    app.run(debug=True)
