import cv2
import numpy as np
import os

# ---------------------------
# 1. Load Video
# ---------------------------

cap = cv2.VideoCapture("../data/videos/video4.mp4")

if not cap.isOpened():
    print("❌ Failed to read video")
    exit()

print("✅ Video loaded")

# Get FPS for normal playback
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 25

delay = int(1000 / fps)

# ---------------------------
# 2. Select ROI (Drawer Area)
# ---------------------------

ret, first_frame = cap.read()
if not ret:
    print("❌ Cannot read first frame")
    exit()

roi = cv2.selectROI("Select Drawer Region", first_frame, False, False)
cv2.destroyWindow("Select Drawer Region")

x, y, w, h = roi
x1, y1 = int(x), int(y)
x2, y2 = int(x + w), int(y + h)

print("Drawer Coordinates:", x1, y1, x2, y2)

# Reset video to start
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

previous_gray = None
frame_counter = 0
drawer_open = False

print("Press 'q' to quit")

# ---------------------------
# 3. Process Video
# ---------------------------

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Draw ROI rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Extract drawer region
    roi_frame = frame[y1:y2, x1:x2]

    gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    if previous_gray is None:
        previous_gray = gray
        continue

    # Compute difference
    diff = cv2.absdiff(previous_gray, gray)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    change_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:  # ignore small noise
            change_area += area

    # Debug print (important for tuning)
    print("Change Area:", change_area)

    # Multi-frame confirmation
    if change_area > 3000:
        frame_counter += 1
    else:
        frame_counter = 0

    # Confirm drawer open
    if frame_counter >= 3 and not drawer_open:
        drawer_open = True
        print("🚨 Drawer OPEN detected")

    # Confirm drawer closed
    if change_area < 1000 and drawer_open:
        drawer_open = False
        print("✅ Drawer CLOSED detected")

    previous_gray = gray

    # Show frame
    cv2.imshow("Drawer Monitoring", frame)

    if cv2.waitKey(delay) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()