import cv2
import argparse
import numpy as np
from ultralytics import YOLO

# Global variables for calibration
calibration_points = []

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        calibration_points.append([x, y])
        print(f"Point added: {x}, {y}")

def calibrate_zone(source_path):
    """
    Step 1: Open video stream.
    Step 2: User clicks points to define the polygon.
    Step 3: Press 'c' to finish and print coordinates.
    Step 4: Press 'r' to reset points.
    Step 5: Press 'q' to quit without saving.
    """
    global calibration_points
    cap = cv2.VideoCapture(source_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video source {source_path}")
        return None

    cv2.namedWindow("Calibration - Click points to define zone")
    cv2.setMouseCallback("Calibration - Click points to define zone", mouse_callback)

    print("--- Calibration Mode ---")
    print("1. Click on the video to define the polygon points for the cash counter.")
    print("2. Press 'c' when done to print the coordinates.")
    print("3. Press 'r' to reset points.")
    print("4. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            # Loop video if it ends
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        # Draw existing points and lines
        if len(calibration_points) > 0:
            pts = np.array(calibration_points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=False, color=(0, 255, 255), thickness=2)
            for pt in calibration_points:
                cv2.circle(frame, tuple(pt), 5, (0, 0, 255), -1)

        cv2.imshow("Calibration - Click points to define zone", frame)
        
        key = cv2.waitKey(25) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            print("\n--- Calibration Complete ---")
            print(f"Copy these coordinates into your script or use them:")
            print(f"counter_zone_points = {calibration_points}")
            print("----------------------------\n")
            
            # Draw closed polygon to show result before exiting
            if len(calibration_points) > 2:
                pts = np.array(calibration_points, np.int32)
                cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.imshow("Calibration - Click points to define zone", frame)
                cv2.waitKey(2000) # Show for 2 seconds
            
            cap.release()
            cv2.destroyAllWindows()
            return calibration_points
        elif key == ord('r'):
            calibration_points = []
            print("Points reset.")

    cap.release()
    cv2.destroyAllWindows()
    return None

def detect_person_behind_counter(source_path=0, counter_zone_points=None):
    """
    Detects people in a specific zone (e.g., behind a cash counter) using YOLOv8.
    """
    
    # Load the YOLOv8 model
    # 'yolov8n.pt' is the nano model, fast and reasonably accurate for people.
    # If you have trained a custom model on your dataset, change this to your model path, e.g., 'path/to/best.pt'
    try:
        model = YOLO('yolov8n.pt') 
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # defined zone (polygon) for the cash counter
    if counter_zone_points is None:
        # Dummy polygon - Replace these coordinates with points relevant to your camera view!
        # You can use tools like https://roboflow.github.io/polygonzone/ to find coordinates
        print("Warning: Using dummy zone coordinates. Run with --calibrate to define your own zone.")
        counter_zone_points = np.array([[100, 100], [500, 100], [500, 400], [100, 400]], np.int32)
    else:
        counter_zone_points = np.array(counter_zone_points, np.int32)

    # Open video source
    cap = cv2.VideoCapture(source_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video source {source_path}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Run YOLOv8 inference on the frame
        # classes=0 limits detection to 'person' class only (COCO class 0 is person)
        results = model(frame, classes=0, verbose=False) 
        
        # Process detections
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Calculate center bottom of the bounding box (feet position)
                # This is better for checking if they are standing "in" the zone
                feet_x = int((x1 + x2) / 2)
                feet_y = int(y2)
                
                # Check if the person's feet are inside the counter zone
                is_inside = cv2.pointPolygonTest(counter_zone_points, (feet_x, feet_y), False)
                
                color = (0, 255, 0) # Green if outside
                label = "Person"
                
                if is_inside >= 0:
                    color = (0, 0, 255) # Red if inside (behind counter)
                    label = "ALERT: Behind Counter"
                    
                    # Alert logic can go here
                    # print("Alert: Person detected behind counter!")

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
        # Draw the counter zone polygon
        cv2.polylines(frame, [counter_zone_points], isClosed=True, color=(255, 255, 0), thickness=2)
        
        # Display the frame
        cv2.imshow('Cash Counter Detection', frame)
        
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Detect person behind cash counter.')
    parser.add_argument('--source', type=str, default='services/1000057185.mp4', help='Video source path or camera index (default: services/1000057185.mp4)')
    parser.add_argument('--calibrate', action='store_true', help='Run in calibration mode to define the zone')
    args = parser.parse_args()

    # Parse source
    source = args.source
    if source.isdigit():
        source = int(source)

    zone_points = None
    if args.calibrate:
        print(f"Starting calibration on source: {source}...")
        zone_points = calibrate_zone(source)
        if zone_points:
            print("Using calibrated points for detection session...")
        else:
            print("Calibration cancelled or failed. Exiting.")
            exit()

    print(f"Starting detection on source: {source}... Press 'q' to quit.")
    detect_person_behind_counter(source_path=source, counter_zone_points=zone_points)
