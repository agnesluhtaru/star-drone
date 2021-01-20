"""
This file contains code from OpenCV calibration tutorial:
https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
"""
import time

import numpy as np
import cv2
import easytello


NUMBER_OF_IMAGES = 100
CHESS_X = 6
CHESS_Y = 8


def init_drone():
    drone = easytello.Tello()
    drone.send_command('streamon')


def take_images(vid=0):
    cap = cv2.VideoCapture(DRONE_STREAM)
    for i in range(NUMBER_OF_IMAGES * 10):
        ret, frame = cap.read()
        cv2.imshow("Calibration", frame)
        if i % 10 == 0:
            print(i / 10)
            cv2.imwrite(f'localization_module/calibration_images/{int(i / 10)}.png', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def chessboard():
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objp = np.zeros((CHESS_X * CHESS_Y, 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHESS_Y, 0:CHESS_X].T.reshape(-1, 2)

    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    for i in range(int(NUMBER_OF_IMAGES)):
        print(i)
        file_name = f'localization_module/calibration_images/{i}.png'
        image = cv2.imread(file_name)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, (CHESS_Y, CHESS_X), None)

        if ret:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(image, (CHESS_Y, CHESS_X), corners2, ret)
            cv2.imshow('img', img)
            cv2.waitKey(5)

    cv2.destroyAllWindows()
    return objpoints, imgpoints, gray


def calibrate_camera(objpoints, imgpoints, gray):
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    np.savetxt('localization_module/calibration_results/camera-matrix.txt', mtx)
    np.savetxt('localization_module/calibration_results/dist.txt', dist)
    print(ret)


if __name__ == '__main__':
    #init_drone()
    #take_images(DRONE_STREAM)
    objpoints, imgpoints, gray = chessboard()
    calibrate_camera(objpoints, imgpoints, gray)
