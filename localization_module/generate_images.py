import cv2
import numpy as np
import matplotlib.pyplot as plt


def generate_marker_image(number, size, dictionary):
    marker_image = np.zeros((size, size), dtype=np.uint8)
    marker_image = cv2.aruco.drawMarker(dictionary, number, size, marker_image, 1)
    marker_image = cv2.copyMakeBorder(marker_image, 50, 50, 50, 50, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    #marker_image = cv2.copyMakeBorder(marker_image, 5, 5, 5, 5, cv2.BORDER_CONSTANT, None, (0, 0, 0))
    cv2.imwrite(f'markers_images/marker{number}-{size}.png', marker_image)
    return marker_image


if __name__ == '__main__':
    dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    images = []
    for i in range(1, 6):
        images += [generate_marker_image(i, 200, dictionary)]

    _, axs = plt.subplots(1, 3, figsize=(12, 12))
    axs = axs.flatten()
    for img, ax in zip(images, axs):
        ax.imshow(img, cmap='gray')
    plt.show()
