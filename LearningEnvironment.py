import cv2
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import scipy
from datetime import datetime
import os


def create_rand_image():
    # image
    x_size = 1600
    y_size = 800
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
        array[int(spline(i) + 100), i] = 255
    # plot the graph
    cv2.imshow("Canvas", array)
    cv2.waitKey(0)

    # save array as image
    curr_time = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    name = "D:\Images\Image_" + curr_time + ".png"
    cv2.imwrite(name, array)  # imwrite(filename, img[, params])

    return array


create_rand_image()
