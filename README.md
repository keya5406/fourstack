# Person Detection Behind Cash Counter

This project detects people in a specified area (behind a cash counter) using CCTV footage and YOLOv8.

## Setup

1.  **Install Python**: Ensure Python is installed and added to your PATH.
2.  **Install Dependencies**:
    ```bash
    pip install opencv-python ultralytics numpy
    ```

## Usage

### Using Webcam (Default)
Run the script directly:
```bash
python detect.py
```

### Using Your Own Video Dataset (CCTV Footage)
I found your video in the `services/` directory. You can run it like this:

**1. Calibrate the zone (Click points on the screen):**
```bash
python detect.py --source "services/1000057185.mp4" --calibrate
```

**2. Run detection:**
```bash
python detect.py --source "services/1000057185.mp4"
```

*Note: In the calibration window, click to draw points around the cash counter, press 'c' to finish, and 'q' to quit.*


### Defining the Cash Counter Area
The script uses a hardcoded polygon to define the "behind counter" area. You **must** update this to match your specific camera view.

1.  Open `detect.py`.
2.  Find the `counter_zone_points` variable inside `detect_person_behind_counter`.
3.  Update the coordinates `[[x1, y1], [x2, y2], ...]` to match the pixel coordinates of your counter area.
    - Top-left is (0,0).
    - You can use tools like [Roboflow PolygonZone](https://roboflow.github.io/polygonzone/) to find the coordinates on a screenshot of your video.

## Training on Custom Dataset
If you want to train a custom YOLO model on your labeled dataset:

1.  Prepare your dataset in YOLO format (images and labels).
2.  Create a `data.yaml` file pointing to your dataset.
3.  Run training:
    ```python
    from ultralytics import YOLO
    
    model = YOLO('yolov8n.pt') 
    results = model.train(data='path/to/data.yaml', epochs=100, imgsz=640)
    ```
4.  Update `detect.py` to use your trained model path: `model = YOLO('runs/detect/train/weights/best.pt')`
