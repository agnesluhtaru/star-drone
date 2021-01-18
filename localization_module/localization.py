import cv2
import numpy as np

MARKER_LENGTH = 20  # cm
running = True


def marker_detection(frame, dictionary, parameters):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    marker_corners, marker_ids, rejected_candidates = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)
    image = cv2.aruco.drawDetectedMarkers(gray, marker_corners, marker_ids)
    return marker_corners, marker_ids, image


def get_translation_vectors(marker_image, dictionary, parameters, camera_matrix, dist):
    corners, ids, image = marker_detection(marker_image, dictionary, parameters)
    rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, MARKER_LENGTH, camera_matrix, dist)
    return ids, tvecs, image


def localization():
    """
    Join all marker detection logic, can be started in separate thread
    """
    global running

    dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters_create()

    camera_matrix = np.loadtxt('calibration_results/camera-matrix.txt')
    dist = np.loadtxt('calibration_results/dist.txt')

    cap = cv2.VideoCapture(0)
    while running:
        ret, markerImage = cap.read()
        ids, tvecs, image = get_translation_vectors(markerImage, dictionary, parameters, camera_matrix, dist)
        if tvecs is not None:
            print(f'x: {tvecs[0,0,0]}, y: {tvecs[0,0,1]}, z: {tvecs[0,0,2]}')
        cv2.imshow("DETECTION WINDOW", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False


if __name__ == '__main__':
    localization()
