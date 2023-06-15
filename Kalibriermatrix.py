import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy
from datetime import datetime
import tkinter
from tkinter import filedialog
from skimage.morphology import skeletonize


# function to get the pixel cords
# on mouseclick
def click_event(event, x, y, flags, params):
    global xi
    global yi
    # checking for event
    if event == cv2.EVENT_LBUTTONDOWN:
        xi = x
        yi = y


# global var
pixel_cords = np.ones((3, 4))
real_cords = np.ones((4, 4))
test_cord = np.ones((3, 1))
xi, yi = 0, 0
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
# for i in range(4):
#     print("Point" + str(i + 1) + " x :")
#     real_cords[0, i] = input()
#     print("Point" + str(i + 1) + " y :")
#     real_cords[1, i] = input()
#     print("Point" + str(i + 1) + " z :")
#     real_cords[2, i] = input()
real_cords = np.array([[112.06, 210.75, 456.48, 629.8],
                       [663.58, 647.66, 621.83, 765.42],
                       [-27.28, -19.77, -38.8, -46.59]])
print(real_cords)

inv_pixel_cords = np.linalg.pinv(pixel_cords)
k = real_cords.dot(inv_pixel_cords)
print("Kalibriermatrix",k)

# verify
cv2.imshow('image', img)
cv2.setMouseCallback('image', click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()
test_cord[0, 0] = xi
test_cord[1, 0] = yi
test_cord[2, 0] = 1
print(test_cord)
p = k.dot(test_cord)
print(p)
