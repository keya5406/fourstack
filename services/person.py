from ultralytics import YOLO
import cv2
import json
import math

# Load YOLO
model = YOLO("yolov8n.pt")

# Load Drawer Coordinates from JSON
with open("drawer_coordinates.json") as f:
    data = json.load(f)

drawer_box = (
    data["drawer"]["x1"],
    data["drawer"]["y1"],
    data["drawer"]["x2"],
    data["drawer"]["y2"]
)

# Function to check proximity
def is_near(person_box, drawer_box):

    px1, py1, px2, py2 = person_box
    dx1, dy1, dx2, dy2 = drawer_box

    person_center = ((px1+px2)//2, (py1+py2)//2)
    drawer_center = ((dx1+dx2)//2, (dy1+dy2)//2)

    distance = math.sqrt(
        (person_center[0]-drawer_center[0])**2 +
        (person_center[1]-drawer_center[1])**2
    )

    return distance < 200   # adjust later

# Video Input
cap = cv2.VideoCapture("services/1000057185.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    person_near = False

    for box in results[0].boxes:
        cls = int(box.cls[0])
        if model.names[cls] == "person":

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            person_box = (x1,y1,x2,y2)

            # Draw person
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(frame,"Person",(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)

            if is_near(person_box, drawer_box):
                person_near = True

    # Draw Drawer
    dx1, dy1, dx2, dy2 = drawer_box
    cv2.rectangle(frame,(dx1,dy1),(dx2,dy2),(255,0,0),2)
    cv2.putText(frame,"Drawer",(dx1,dy1-10),
                cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)

    # Status
    if person_near:
        status = "Person Near Drawer"
        color = (0,255,0)
    else:
        status = "No One Near Drawer"
        color = (0,0,255)

    cv2.putText(frame,status,(50,50),
                cv2.FONT_HERSHEY_SIMPLEX,1,color,2)

    cv2.imshow("Presence Detection", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()