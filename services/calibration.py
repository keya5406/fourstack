import cv2
import json
import os
import numpy as np
import base64

_temp_coordinates = None
COORDINATE_FILE = "drawer_coordinates.json"
FRAME_FILE = "temp_frame.jpg"


def save_frame_from_base64(base64_data):
    """
    Converts base64 image from frontend into an image file.
    """

    header, encoded = base64_data.split(",", 1)
    image_bytes = base64.b64decode(encoded)

    with open(FRAME_FILE, "wb") as f:
        f.write(image_bytes)

    return FRAME_FILE


def start_calibration_from_frame():
    """
    Opens OpenCV ROI selector using saved frame.
    """

    global _temp_coordinates

    if not os.path.exists(FRAME_FILE):
        print("Frame file not found.")
        return None

    frame = cv2.imread(FRAME_FILE)

    roi = cv2.selectROI(
        "Select Drawer Area",
        frame,
        fromCenter=False,
        showCrosshair=True
    )

    cv2.destroyAllWindows()

    x, y, w, h = roi

    if w == 0 or h == 0:
        return None

    _temp_coordinates = {
        "x1": int(x),
        "y1": int(y),
        "x2": int(x + w),
        "y2": int(y + h),
        "width": int(w),
        "height": int(h)
    }

    return _temp_coordinates


def save_coordinates():
    global _temp_coordinates

    if _temp_coordinates is None:
        return False

    with open(COORDINATE_FILE, "w") as f:
        json.dump(_temp_coordinates, f, indent=4)

    return True