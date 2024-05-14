import cv2
import datetime
import json
import requests

from enum import Enum
from playsound import playsound


class CameraMode(Enum):
    ARRIVAL = 1
    DEPARTURE = 2


class Crate:
    def __init__(self, qr_code, scan_date):
        self.qr_code = qr_code
        self.scan_date = scan_date


class Station:
    def __init__(self, id, name):
        self.id = id
        self.name = name


station = Station(1, 'Assembly')
current_crates = []
processed_crates = []


def send_message_start(order_id):
    global station
    if order_id is None:
        return

    url = 'http://localhost:3000/api/v1/events/start'
    headers = {'Content-type': 'application/json'}
    data = {
        "orderId": order_id,
        "stationId": station.id,
        "startTime": datetime.datetime.now()
    }
    data_json = json.dumps(data, default=str)
    requests.post(url, data=data_json, headers=headers)


def send_message_end(order_id):
    global station
    if order_id is None:
        return

    url = 'http://localhost:3000/api/v1/events/end'
    headers = {'Content-type': 'application/json'}
    data = {
        "orderId": order_id,
        "stationId": station.id,
        "endTime": datetime.datetime.now()
    }
    data_json = json.dumps(data, default=str)
    requests.post(url, data=data_json, headers=headers)


def is_crate_allowed_at_station(order_id):
    global station
    if order_id is None:
        return False

    url = 'http://localhost:3000/api/v1/station/check'
    headers = {'Content-type': 'application/json'}
    data = {
        "orderId": order_id,
        "station": station.id
    }
    data_json = json.dumps(data)
    response = requests.post(url, data=data_json, headers=headers)

    if response is None or response.json()['isAtCorrectStation'] is None:
        return False

    return response.json()['isAtCorrectStation']


def is_current_crate(qr_info):
    if qr_info is None:
        return False

    global current_crates
    if not current_crates:
        # No current crates
        return False

    if any(current_crate.qr_code == qr_info for current_crate in current_crates):
        # Found crate
        return True

    # Did not find crate
    return False


def is_processed_crate(qr_info):
    if qr_info is None:
        return False

    global processed_crates
    if any(processed_crate.qr_code == qr_info for processed_crate in processed_crates):
        # Found crate
        return True

    # Did not find crate
    return False


def process_crate_arrival(order_id):
    global station
    global current_crates
    scan_date = datetime.datetime.now()
    print('Order', order_id, 'arriving at station', station.name, 'at', scan_date)

    if not is_current_crate(order_id):
        # update local crate cache
        current_crates.append(Crate(order_id, scan_date))
        # update backend
        send_message_start(order_id)
        playsound('./sounds/success_bell.mp3', False)


def process_crate_departure(order_id):
    global station
    global current_crates
    scan_date = datetime.datetime.now()
    print('Order', order_id, 'departing from station', station.name, 'at', scan_date)

    if is_current_crate(order_id):
        # update local crate cache
        current_crate = next(current_crate for current_crate in current_crates if current_crate.qr_code == order_id)
        processed_crates.append(Crate(current_crate.qr_code, current_crate.scan_date))
        current_crates.remove(current_crate)
        # update backend
        send_message_end(order_id)
        playsound('./sounds/success_bell.mp3', False)


# Function to detect faces and apply color overlay to the bounding box area
def detect_and_color_overlay_bounding_box(frame):
    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect faces in the grayscale frame
    faces = face_classifier.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5, minSize=(40, 40))
    # Apply color overlay to the bounding box area for each detected face
    for (x, y, w, h) in faces:
        # Define the color for the overlay (BGR format)
        # Yellow color (blue, green red)
        overlay_color = (128, 128, 128)  # (0, 255, 255)
        # Draw a filled rectangle (overlay) on the frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), overlay_color, -1)
    return frame


print('Station:', station.name)
print("Press q to close window")

camera_id = 0
delay = 1
window_name = 'QR Code Detector'
camera_mode = CameraMode.ARRIVAL

# Load the face classifier
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

qcd = cv2.QRCodeDetector()
cap = cv2.VideoCapture(camera_id)

while True:
    ret, frame = cap.read()

    if ret:
        # Detect faces and apply color overlay to the bounding box area
        frame = detect_and_color_overlay_bounding_box(frame)
        # Display the processed frame
        cv2.imshow(window_name, frame)

        ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
        if ret_qr:
            for s, p in zip(decoded_info, points):
                # decoding successful
                if s:
                    color_green = (0, 255, 0)
                    frame = cv2.polylines(frame, [p.astype(int)], True, color_green, 6)

                    # for arrival camera - new crate arrival
                    if not is_current_crate(s) and not is_processed_crate(s):
                        if is_crate_allowed_at_station("A_2663577"):
                            process_crate_arrival(s)
                        else:
                            # TODO: Show red light
                            playsound('./sounds/error.mp3', False)

                    # for departure camera - already processed crate arrives
                    if not is_current_crate(s) and is_processed_crate(s):
                        print("Crate has already been processed at this station")

                    if not is_current_crate(s) and not is_processed_crate(s):
                        # TODO: Show red light
                        playsound('./sounds/error.mp3', False)
                        print("Crate has not been processed at this station! No arrival has been detected previously.")

                    if is_current_crate(s):
                        process_crate_departure(s)

        cv2.imshow(window_name, frame)

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cv2.destroyWindow(window_name)
