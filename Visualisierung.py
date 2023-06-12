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


def visualise(img, movement_string, x_start, y_start):
    x = x_start
    y = y_start
    step_size = 1
    img[y, x] = [0, 0, 255]

    cv2.imshow("Linie", img)
    #cv2.imshow("State", state)
    cv2.waitKey(100)
    for char in movement_string:
        cv2.imshow("Linie", img)
        #cv2.imshow("State", state)
        cv2.waitKey(100)
        if char == 'r':
            x += step_size
        elif char == 'l':
            x -= step_size
        elif char == 'u':
            y += step_size
        elif char == 'd':
            y -= step_size
        img[y, x] = [0, 0, 255]
