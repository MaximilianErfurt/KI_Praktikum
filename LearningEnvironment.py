import cv2
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import scipy
from datetime import datetime
import tkinter
from tkinter import filedialog
from skimage.morphology import skeletonize

###### Why are these imports here? Do we need them or can they go
# import matplotlib.pyplot as plot
# from PIL import Image
# import os

# Method to create images with random splines
# 2 Modes:
# Mode = 1 save the global_environment in chosen folder
# Mode = 0 return as array


def create_rand_image(mode):
    # global_environment
    x_size = 2736
    y_size = 1824
    array = np.zeros((y_size, x_size), dtype='uint8', )

    # generating random points
    x = np.arange(x_size/12, x_size, x_size / 12, int)
    x_start = np.arange(0, int(x[0]), int(x[0])/3)
    x_end = np.arange(x[-1] + int(x[0]) / 3, x_size, int(x[0]) / 3)
    x = np.concatenate([x_start, x, x_end])
    y = np.random.randint(0, y_size / 2, len(x))
    # print(len(y))

    # fix first and last three spline points to make it more realistic
    y[0] = y[1] = y[2] = y[-1] = y[-2] = y[-3] = y_size/4

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

        # save array as global_environment
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


# function takes a boolean array and returns a list of global_environment coordinates, starting on the left side of
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


class State:
    # Constructor parameters are:
    # - The Global environment Matrix of the current Spline (as 2D int array)
    # - the goal path returned by extract_path() function
    # - the current midpoint position of the two contacts
    # - current orientation of contacts, as a value of 0 - 7
    # - current local goal as index to goal_path list
    def __init__(self, global_environment: npt.ArrayLike, goal_path: list[tuple[int, int]], contact_position: tuple[int, int], contact_orientation: int, local_goal: int):
        self.local_goal = goal_path[local_goal]
        self.contact_orientation = contact_orientation
        self.contact_position = contact_position
        self.local_environment = np.zeros((5, 5), dtype=int)

        # Key for filling the local environment matrix:
        # - 0 = empty space
        # - 1 = wire
        # (- 2 = current local goal. This is only implemented in the __repr__ method further down)
        # - 3 = left contact
        # 4 = right contact
        for i in range(5):
            for j in range(5):
                self.local_environment[j, i] = int(global_environment[self.contact_position[0] - 2 + j, self.contact_position[1] - 2 + i])
        match self.contact_orientation:
            # 3 denotes the left contact
            # 4 denotes the right contact
            case 0:
                # left contact center top
                # right contact center bottom
                self.local_environment[0, 2] = 3
                self.local_environment[4, 2] = 4
            case 1:
                # left contact top right
                # right contact bottom left
                self.local_environment[0, 4] = 3
                self.local_environment[4, 0] = 4
            case 2:
                # left contact center right
                # right contact center left
                self.local_environment[2, 4] = 3
                self.local_environment[2, 0] = 4
            case 3:
                # left contact bottom right
                # right contact top left
                self.local_environment[4, 4] = 3
                self.local_environment[0, 0] = 4
            case 4:
                # left contact center bottom
                # right contact center top
                self.local_environment[4, 2] = 3
                self.local_environment[0, 2] = 4
            case 5:
                # left contact bottom left
                # right contact top right
                self.local_environment[4, 0] = 3
                self.local_environment[0, 4] = 4
            case 6:
                # left contact center left
                # right contact center right
                self.local_environment[2, 0] = 3
                self.local_environment[2, 4] = 4
            case 7:
                # left contact top left
                # right contact bottom right
                self.local_environment[0, 0] = 3
                self.local_environment[4, 4] = 4
            case _:
                print("Invalid contact orientation provided! Use numbers from 0-7")

    def __repr__(self):
        # reproduces the 5x5 local environment matrix and tries to add the local goal (2) to it.
        # I do this because I do not want the local goal in the actual environment matrix, but I do want it printed
        repr_matr = np.copy(self.local_environment)
        try:
            repr_matr[self.local_goal[0] - self.contact_position[0] + 2, self.local_goal[1] - self.contact_position[1] + 2] = 2
        except IndexError:
            print("Local Goal outside of Local Environment!\n\n")

        # I am aware that the following line of code is a crime against humanity, but I won't be doing anything about it
        return "{}:\n\n{} {} {} {} {}\n{} {} {} {} {}\n{} {} {} {} {}\n{} {} {} {} {}\n{} {} {} {} {}\n\n".format(type(self).__name__, repr_matr[0, 0], repr_matr[0, 1], repr_matr[0, 2], repr_matr[0, 3], repr_matr[0, 4], repr_matr[1, 0], repr_matr[1, 1], repr_matr[1, 2], repr_matr[1, 3], repr_matr[1, 4], repr_matr[2, 0], repr_matr[2, 1], repr_matr[2, 2], repr_matr[2, 3], repr_matr[2, 4], repr_matr[3, 0], repr_matr[3, 1], repr_matr[3, 2], repr_matr[3, 3], repr_matr[3, 4], repr_matr[4, 0], repr_matr[4, 1], repr_matr[4, 2], repr_matr[4, 3], repr_matr[4, 4])

    # def move_right(self):

    # def move_left(self)

    # def move_up(self)

    # def move_down(self):

    # def rotate_cw(self):

    # def rotate_ccw(self):
