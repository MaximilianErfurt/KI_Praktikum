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
from skimage.morphology import skeletonize


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
    # plt.show()

    # merge into array
    for i in range(x_size):
        array[int(spline(i) + 175), i] = 255

    # fill up empty space
    kernel = np.ones((7, 7), np.uint8)
    array = cv2.dilate(array, kernel, iterations=1)

    # *255 is only needed if mode == 1 -> moved it into the if statement
    array = skeletonize(array)

    # loop to change all the values of the first 3 and last 3 columns to 0, as those sometimes turn out buggy
    for i in range(3):
        array[:, i] = array[:, - i - 1] = np.zeros(array.shape[0])

    # plot the graph
    # cv2.imshow("Canvas", array)
    # cv2.waitKey(0)

    # get folder and save
    if mode == 1:
        tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
        folder_path = filedialog.askdirectory()  # ask user for folder to save in


        # save array as image
        curr_time = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        name = folder_path + "/Image" + curr_time + ".png"
        array = array * 255
        cv2.imwrite(name, array)  # imwrite(filename, img[, params])

    # return array
    if mode == 0:
        array_bool = np.zeros((array.shape[0], array.shape[1]), dtype=bool)
        # convert to bool for performance
        # numpy array conversion to bool doesn't work properly, so I'm doing it manually
        for i in range(array.shape[1]):
            for j in range(array.shape[0]):
                if not(array[j, i] == 0):
                    array_bool[j, i] = True
        return array_bool


# function takes a boolean array and returns a list of image coordinates, starting on the left side of
# the spline and ending on the right side
def extract_path(array) -> list[(int, int)]:
    height = array.shape[0]
    width = array.shape[1]

    path = list()

    startpoint = (int, int)
    endpoint_found = False

    # loop to find the startpoint of spline
    # start iterating columns in top-left corner
    for i in range(width):
        startpoint_found = False
        # work your way through the rows -> j = row, i = column
        for j in range(height):
            if array[j, i]:
                # once part of the path has been found, check if it is truly the startpoint of the path. Do this by
                # checking all values in a 3x3 grid around the found point of the path. If only one is found,
                # it means the initially found point is the startpoint. This assumes column 0 will never have any true
                # values -> fix required if it does
                found_trues = 0
                for k in range(3):
                    for l in range(3):
                        # ignore the midpoint
                        if not (l == 1 and k == 1):
                            if array[j - 1 + l, i - 1 + k]:
                                found_trues += 1
                if found_trues == 1:
                    # value of 1 means startpoint has been found
                    startpoint_found = True
                    startpoint = (j, i)

                    # break out of row loop
                    break
        # break out of column loop if startpoint has been found
        if startpoint_found:
            break

    if startpoint == (0, 0):
        print("No Startpoint could be found! Returning empty list.")
        return path
    else:
        path.append(startpoint)

    # extract every element
    iteration = 0
    while True:
        new_point_found = False
        current_point = path[iteration]
        if not (iteration == 0):
            previous_point = path[iteration - 1]
        else:
            previous_point = (None, None)

        for i in range(3):
            for j in range(3):
                # ignore the midpoint
                if not (j == 1 and i == 1):
                    point_checked = (current_point[0] - 1 + j, current_point[1] - 1 + i)
                    # check if a point is found and, if yes, check that it isn't the point from the previous iteration
                    if array[point_checked[0], point_checked[1]] and not (point_checked == previous_point):
                        new_point_found = True
                        path.append(point_checked)
                        break
            if new_point_found:
                break

        # if no new point was found, break the while loop. List is now complete
        if not new_point_found:
            endpoint_found = True
            break

        iteration += 1

    if not endpoint_found:
        print("No spline endpoint could be found! Returning potentially incomplete path")
    return path







