import threading
import time

import cv2
import easytello
import numpy as np

MARKER_LENGTH = 19  # cm
DRONE_STREAM = 'udp://192.168.10.1:11111'

MARKER_LOCATIONS = {4: [89, 1, 434, 1], 5: [192, 1, 434, 1], 2: [312, 1, 434, 1]}
N = 30


class Localization:
    def __init__(self):
        self.running = True
        self.dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters_create()
        self.camera_matrix = np.loadtxt('localization_module/calibration_results/camera-matrix.txt')
        self.dist = np.loadtxt('localization_module/calibration_results/dist.txt')
        self.cap = cv2.VideoCapture(DRONE_STREAM)
        self.location = None
        self.loc_thread = threading.Thread(target=self.localization)
        self.loc_thread.start()

    def get_xy(self):
        if self.location is not None:
            return int(self.location[0, 0]), int(self.location[0, 2])
        return self.location

    def localization(self):
        moving_averaging = []
        count = 0
        while self.running:
            count += 1
            ret, marker_image = self.cap.read()
            image, moving_averaging = self.get_location_estimate(marker_image, moving_averaging)
            image = cv2.putText(image, str(count), (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("DETECTION WINDOW", image)
            time.sleep(0.01)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False

    def get_location_estimate(self, markerImage, moving_averaging):
        ids, tvecs, rotation_matrixes, image = self.get_translation_vectors(markerImage, self.dictionary,
                                                                            self.parameters,
                                                                            self.camera_matrix,
                                                                            self.dist)
        if tvecs is not None and rotation_matrixes is not None:
            estimates = []
            for estimate in range(len(ids[0])):
                translation_vector = np.asarray(tvecs[0, estimate]).reshape((3, 1))
                vector = np.zeros((4, 1))
                vector[0:3] = translation_vector
                vector[3] = 1
                # matrix = np.zeros((4, 4))
                # matrix[0:3, 0:3] = rotation_matrixes[estimate]
                # matrix[3, 3] = 1
                # joint = np.matmul(matrix.T, vector)
                robo_location = -vector.T + MARKER_LOCATIONS[ids[0, estimate]]
                estimates.append(robo_location)
            averaged = sum(estimates) / len(estimates)
            moving_averaging.append(averaged)
            if len(moving_averaging) > N:
                moving_averaging.pop(0)
        if len(moving_averaging) >= N:
            self.location = sum(moving_averaging) / len(moving_averaging)
            # if count % 20 == 0:
            # print(f'x: {location[0, 0]}, z: {location[0, 2]}')
        return image, moving_averaging

    def marker_detection(self, frame, dictionary, parameters):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        marker_corners, marker_ids, rejected_candidates = cv2.aruco.detectMarkers(gray, dictionary,
                                                                                  parameters=parameters)
        image = cv2.aruco.drawDetectedMarkers(gray, marker_corners, marker_ids)
        return marker_corners, marker_ids, image

    def get_translation_vectors(self, marker_image, dictionary, parameters, camera_matrix, dist):
        corners, ids, image = self.marker_detection(marker_image, dictionary, parameters)
        rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, MARKER_LENGTH, camera_matrix, dist)
        matrixes = []

        if rvecs is not None:
            for r in rvecs:
                rotation_matrix, jacobian = cv2.Rodrigues(r[0])
                matrixes.append(rotation_matrix)
        else:
            matrixes.append(None)
        return ids, tvecs, matrixes, image
