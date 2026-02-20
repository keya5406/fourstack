import os
import base64
import json
import cv2
import numpy as np
from typing import Dict

# assumes encoded JSON lives here by default
ENC_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "encodings", "encoded_images.json")


    # Convert a base64 string back into a BGR numpy image
def decode_string_to_image(b64: str) -> np.ndarray:
    data = base64.b64decode(b64)
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


    # Load the JSON file that maps filename->base64 string
def load_encodings(path: str = ENC_JSON) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def display_all(path: str = ENC_JSON) -> None:
    encs = load_encodings(path)
    for name, b64 in encs.items():
        img = decode_string_to_image(b64)
        if img is None:
            print(f"failed to decode {name}")
            continue
        cv2.imshow(name, img)
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyWindow(name)
        if key == ord("q"):
            break


def save_all(path: str = ENC_JSON, out_dir: str = None) -> None:
    encs = load_encodings(path)
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "decoded")
    os.makedirs(out_dir, exist_ok=True)
    for name, b64 in encs.items():
        img = decode_string_to_image(b64)
        if img is None:
            continue
        cv2.imwrite(os.path.join(out_dir, name), img)


if __name__ == "__main__":
    print(f"loading from {ENC_JSON}")
    display_all(ENC_JSON)
