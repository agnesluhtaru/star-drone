import cv2
import numpy as np

MARKER_LENGTH = 200  # unit !!!
running = True


def marker_candidates_detection(frame, dictionary, parameters):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect the markers in the image
    markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)
    # print(markerIds)
    image = cv2.aruco.drawDetectedMarkers(gray, markerCorners, markerIds)
    return image, markerCorners


def estimate_position(corners, markerLength, cameraMatrix, dist):
    rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, markerLength, cameraMatrix, dist)
    print(tvecs)


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
    dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_APRILTAG_25h9)
    parameters = cv2.aruco.DetectorParameters_create()

    markerImage = cv2.imread('test-images/marker33.png')
    image_matrix = np.loadtxt('camera-matrix.txt')
    dist = np.loadtxt('dist.txt')
    # rvecs = np.loadtxt('rvecs.txt')
    # tvecs = np.loadtxt('tvecs.txt')
    cap = cv2.VideoCapture(0)
    while running:
        ret, markerImage = cap.read()
        image, corners = marker_candidates_detection(markerImage, dictionary, parameters)
        estimate_position(corners, 200, image_matrix, dist)
        cv2.imshow("DETECTION WINDOW", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False


if __name__ == '__main__':
    marker_detection()
