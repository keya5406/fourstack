import os
import base64
from typing import Dict

# directory containing images to encode
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "images")


def encode_image_to_string(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def process_folder(folder: str = IMAGES_DIR) -> Dict[str, str]:
    encodings: Dict[str, str] = {}
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"images folder does not exist: {folder}")

    for fname in sorted(os.listdir(folder)):
        if fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            full = os.path.join(folder, fname)
            encodings[fname] = encode_image_to_string(full)
    return encodings


import json


    # Write the encoding dictionary to a JSON file
def save_encodings(encodings: Dict[str, str], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(encodings, f, indent=2)


if __name__ == "__main__":
    results = process_folder()
    for name, enc in results.items():
        print(f"{name}: {enc[:60]}... ({len(enc)} bytes)")

    # by default dump to data/encodings/encoded_images.json
    default_dir = os.path.join(os.path.dirname(__file__), "..", "data", "encodings")
    os.makedirs(default_dir, exist_ok=True)
    json_path = os.path.join(default_dir, "encoded_images.json")
    save_encodings(results, json_path)
    print(f"saved encodings to {json_path}")
