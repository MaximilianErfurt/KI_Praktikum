import cv2
import numpy as np
from skimage.morphology import skeletonize
from skimage import data
import matplotlib.pyplot as plt
from skimage.util import invert
import numpy
from sklearn.metrics import r2_score


# Methode to reduce a picture to its skeleton
def reduce_draht_to_line(draht):
    # original global_environment to grey global_environment
    img_gray = cv2.cvtColor(draht, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("img",img_gray)
    # cv2.waitKey(0)
    # blur global_environment for better edge detection with median blur
    img_blur = cv2.medianBlur(img_gray, 9)
    # cv2.imshow("img",img_blur)
    # cv2.waitKey(0)
    # Canny edge detection
    edges = cv2.Canny(image=img_blur, threshold1=0, threshold2=200)  # Canny Edge Detection
    # cv2.imshow("img",edges)
    # cv2.waitKey(0)
    # reducing the two edges to one centered line
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=10)
    skeleton = skeletonize(edges)

    # fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4),
    #                          sharex=True, sharey=True)
    #
    # #plotting the picture
    # ax = axes.ravel()
    # ax[0].imshow(edges, cmap=plt.cm.gray)
    # ax[0].axis('off')
    # ax[0].set_title('original', fontsize=20)
    # ax[1].imshow(skeleton, cmap=plt.cm.gray)
    # ax[1].axis('off')
    # ax[1].set_title('skeleton', fontsize=20)
    # fig.tight_layout()
    # plt.show()
    # cv2.destroyAllWindows()
    return skeleton


def find_start_point(img):
    x = 16
    y = 280
    while not img[y][x]:
        y += 1
    return x, y


# Method to make a boolean img back to RGB
def back_to_rgb(img):
    height, width = img.shape
    rgb_img = np.zeros((height, width, 3), np.uint8)
    for row in range(height):
        for col in range(width):
            if img[row][col]:
                rgb_img[row][col] = [255, 255, 255]
    return rgb_img


# method to crop an image
def crop_and_flip_image(line, border):
    # crop img
    line = line[120:440, 22:538]
    # add an 3 pixel wide left/right border to the cropped image
    shape = np.shape(line)
    shape2 = (shape[0], shape[1] + border * 2)
    line_border = np.zeros(shape=shape2)
    line_border[:, border:shape2[1] - border] = line
    cv2.imshow("img", line_border)
    cv2.waitKey(0)
    cv2.destroyWindow("img")

    return line_border
