import cv2
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import scipy
from datetime import datetime
import os
import tkinter
from tkinter import filedialog

# Method to create images with random splines
# 2 Modes:
# Mode = 1 save the image in chosen folder
# Mode = 0 return as array
def create_rand_image(mode):
    # image
    x_size = 2736
    y_size = 1824
    array = np.zeros((y_size, x_size), dtype='uint8', )

    # generating random points
    x = np.arange(0, x_size + 10, x_size / 10, int)
    print(len(x))
    y = np.random.randint(0, y_size / 2, len(x))
    print(len(y))

    # generate cubic spline
    spline = scipy.interpolate.CubicSpline(x=x, y=y)

    # plot the spline
    xs = np.arange(0, x_size, 1)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(x, y, 'o', label='data')
    ax.plot(xs, spline(xs), label="S")
    plt.show()

    # merge into array
    for i in range(x_size):
        array[int(spline(i) + 175), i] = 255

    # fill up empty space
    kernel = np.ones((5, 5), np.uint8)
    array = cv2.dilate(array, kernel, iterations=1)
    kernel = np.ones((3, 3), np.uint8)
    array = cv2.erode(array, kernel, iterations=1)

    # plot the graph
    cv2.imshow("Canvas", array)
    cv2.waitKey(0)

    # get folder and save
    if mode == 1:
        tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
        folder_path = filedialog.askdirectory()  # ask user for folder to save in

        # save array as image
        curr_time = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        name = folder_path + "/Image" + curr_time + ".png"
        cv2.imwrite(name, array)  # imwrite(filename, img[, params])

    # return array
    if mode == 0:
        return array
