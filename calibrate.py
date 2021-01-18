"""
This file contains code from OpenCV calibration tutorial:
https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
"""
import time

import numpy as np
import cv2

NUMBER_OF_IMAGES = 100
CHESS_X = 6
CHESS_Y = 8


def take_images():
    cap = cv2.VideoCapture(0)
    for i in range(NUMBER_OF_IMAGES):
        ret, frame = cap.read()
        cv2.imshow("Calibration", frame)
        cv2.imwrite(f'calibration_images/{i}.jpg', frame)
        time.sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def chessboard():
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objp = np.zeros((CHESS_X * CHESS_Y, 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHESS_Y, 0:CHESS_X].T.reshape(-1, 2)

    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    for i in range(NUMBER_OF_IMAGES):
        file_name = f'calibration_images/{i}.png'
        image = cv2.imread(file_name)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (CHESS_Y, CHESS_X), None)

        # If found, add object points, image points (after refining them)
        if ret == True:
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
    np.savetxt('calibration_results/camera-matrix.txt', mtx)
    np.savetxt('calibration_results/dist.txt', dist)


if __name__ == '__main__':
    # take_images()
    objpoints, imgpoints, gray = chessboard()
    calibrate_camera(objpoints, imgpoints, gray)
