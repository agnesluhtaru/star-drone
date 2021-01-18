import sys

import cv2
import numpy as np

MARKER_LENGTH = 200
running = True


def marker_candidates_detection(frame, dictionary, parameters):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect the markers in the image
    markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)
    print(markerIds)
    image = cv2.aruco.drawDetectedMarkers(gray, markerCorners, markerIds)
    return image


def calibrate_camera():
    pass


def estimate_position():
    pass


def generate_marker_image(number, size, dictionary):
    marker_image = np.zeros((200, 200), dtype=np.uint8)
    marker_image = cv2.aruco.drawMarker(dictionary, number, size, marker_image, 1)
    marker_image = cv2.copyMakeBorder(marker_image, 50, 50, 50, 50, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    marker_image = cv2.copyMakeBorder(marker_image, 5, 5, 5, 5, cv2.BORDER_CONSTANT, None, (0, 0, 0))
    cv2.imwrite(f'marker{number}-{size}.png', marker_image)


def marker_detection():
    """
    Join all marker detection logic, can be started in separate thread
    """
    global running
    dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_1000)
    parameters = cv2.aruco.DetectorParameters_create()

    cap = cv2.VideoCapture(0)
    while running:
        ret, markerImage = cap.read()
        image = marker_candidates_detection(markerImage, dictionary, parameters)
        cv2.imshow("DETECTION WINDOW", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False


if __name__ == '__main__':
    marker_detection()
