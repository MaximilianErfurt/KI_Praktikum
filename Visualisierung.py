import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy
from datetime import datetime
import tkinter
from tkinter import filedialog
from skimage.morphology import skeletonize
import tkinter as tk
from matplotlib.animation import FuncAnimation
import LearningEnvironment as Le


def visualise(img, movement_string, x_start, y_start, movements):

    cv2.imshow("Linie", img)
    #cv2.imshow("State", state)
    cv2.waitKey(100)
    for entry in movements:
        cv2.imshow("Linie", img)
        # cv2.imshow("State", state)
        cv2.waitKey(100)
        y = entry[0][0]
        x = entry[0][1]
        current_orientation = Le.contact_orientation_indices[entry[2]]
        img[y - 2 + current_orientation[0][0], x - 2 + current_orientation[0][1]] = [0, 255, 0]
        img[y - 2 + current_orientation[1][0], x - 2 + current_orientation[1][1]] = [255, 0, 0]
        img[y, x] = [0, 0, 255]
