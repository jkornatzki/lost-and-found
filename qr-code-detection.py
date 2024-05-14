import cv2
import datetime

from enum import Enum
from playsound import playsound


class CameraMode(Enum):
    ARRIVAL = 1
    DEPARTURE = 2


class Crate:
    def __init__(self, qr_code, scan_date):
        self.qr_code = qr_code
        self.scan_date = scan_date


station_name = 'Assembly'
current_crates = []
processed_crates = []


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


def process_crate_arrival(qr_info):
    scan_date = datetime.datetime.now()
    print('Order', qr_info, 'arriving at station', station_name, 'at', scan_date)

    global current_crates
    if not is_current_crate(qr_info):
        current_crates.append(Crate(qr_info, scan_date))
        # TODO: Send arrival message to BE
        playsound('./sounds/success_bell.mp3', False)


def process_crate_departure(qr_info):
    scan_date = datetime.datetime.now()
    print('Order', qr_info, 'departing from station', station_name, 'at', scan_date)

    global current_crates
    if is_current_crate(qr_info):
        current_crate = next(current_crate for current_crate in current_crates if current_crate.qr_code == qr_info)
        processed_crates.append(Crate(current_crate.qr_code, current_crate.scan_date))
        current_crates.remove(current_crate)
        # TODO: Send departure message to BE
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


print('Station:', station_name)
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
                if s:
                    # decoding successful
                    color_green = (0, 255, 0)
                    frame = cv2.polylines(frame, [p.astype(int)], True, color_green, 6)

                    # for arrival camera - new crate arrival
                    # TODO: Check crate is supposed to be at this station
                    if not is_current_crate(s) and not is_processed_crate(s):
                        process_crate_arrival(s)

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
