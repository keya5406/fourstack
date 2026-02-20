import cv2
import numpy as np

# -----------------------------
# Step 1: Select Drawer ROI
# -----------------------------

drawer_coords = []
drawing = False

def select_region(event, x, y, flags, param):
    global drawer_coords, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawer_coords = [(x, y)]
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        temp_frame = frame.copy()
        cv2.rectangle(temp_frame, drawer_coords[0], (x, y), (0,255,0), 2)
        cv2.imshow("Select Drawer Region", temp_frame)

    elif event == cv2.EVENT_LBUTTONUP:
        drawer_coords.append((x, y))
        drawing = False
        print("Selected Drawer Coordinates:", drawer_coords)

# Load video
video_path = "your_video.mp4"
cap = cv2.VideoCapture(video_path)

ret, frame = cap.read()
if not ret:
    print("Failed to read video")
    exit()

cv2.namedWindow("Select Drawer Region")
cv2.setMouseCallback("Select Drawer Region", select_region)

print("Drag mouse to select drawer region. Press ESC when done.")

while True:
    temp = frame.copy()
    if len(drawer_coords) == 2:
        cv2.rectangle(temp, drawer_coords[0], drawer_coords[1], (0,255,0), 2)
    cv2.imshow("Select Drawer Region", temp)

    key = cv2.waitKey(1)
    if key == 27:  # ESC key
        break

cv2.destroyWindow("Select Drawer Region")

if len(drawer_coords) != 2:
    print("Drawer region not selected properly.")
    exit()

(x1, y1), (x2, y2) = drawer_coords

# Ensure proper ordering
x1, x2 = min(x1,x2), max(x1,x2)
y1, y2 = min(y1,y2), max(y1,y2)

# -----------------------------
# Step 2: Drawer Monitoring
# -----------------------------

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

drawer_state = "CLOSED"
open_counter = 0
close_counter = 0

MIN_CONSECUTIVE_FRAMES = 5
CONTOUR_AREA_THRESHOLD = 8000  # adjust per location

ret, frame = cap.read()
roi = frame[y1:y2, x1:x2]
prev_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21,21), 0)

print("Monitoring started...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    roi = frame[y1:y2, x1:x2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21,21), 0)

    # Frame difference
    frame_diff = cv2.absdiff(prev_gray, gray)
    thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area

    # Drawer Open Logic
    if max_area > CONTOUR_AREA_THRESHOLD:
        open_counter += 1
        close_counter = 0
    else:
        close_counter += 1
        open_counter = 0

    # Confirm state change
    if open_counter >= MIN_CONSECUTIVE_FRAMES and drawer_state == "CLOSED":
        drawer_state = "OPEN"
        print("Drawer OPEN detected")

    if close_counter >= MIN_CONSECUTIVE_FRAMES and drawer_state == "OPEN":
        drawer_state = "CLOSED"
        print("Drawer CLOSED detected")

    # Display
    cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
    cv2.putText(frame, f"Drawer State: {drawer_state}", (50,50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("Monitoring", frame)

    prev_gray = gray

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()