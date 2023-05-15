import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy
from datetime import datetime
import tkinter
from tkinter import filedialog
from skimage.morphology import skeletonize

# global var
pixel_cords = np.ones((3, 4))
real_cords = np.ones((4, 4))
xi, yi = 0, 0

# function to get the pixel cords
# on mouseclick
def click_event(event, x, y, flags, params):
    global xi
    global yi
    # checking for event
    if event == cv2.EVENT_LBUTTONDOWN:
        xi = x
        yi = y


# reading the image
img = cv2.imread('KalibrierDraht.jpeg', 1)

# for loop to get 4 pixel cords
for i in range(4):
    # setting mouse handler for the image
    # and calling the click_event() function
    cv2.imshow('image', img)
    cv2.setMouseCallback('image', click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # save cords in 4x2 matrix
    pixel_cords[0, i] = xi
    pixel_cords[1, i] = yi
print(pixel_cords)
print(np.linalg.pinv(pixel_cords))


# ask for real cords
for i in range(4):
    print("Point" + str(i+1) + " x :")
    real_cords[0, i] = input()
    print("Point" + str(i + 1) + " y :")
    real_cords[1, i] = input()
    print("Point" + str(i + 1) + " z :")
    real_cords[2, i] = input()
inv_pixel_cords = np.linalg.pinv(pixel_cords)
k = real_cords.dot(inv_pixel_cords)
print(k)


