import cv2
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import scipy


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

    xs = np.arange(0, x_size, 1)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(x, y, 'o', label='data')
    ax.plot(xs, spline(xs), label="S")
    plt.show()

    # merge into image
    for i in range(x_size):
        print(i)
        print(int(spline(i)))
        array[int(spline(i)), i] = 255
        print(array[int(spline(i))][i])



    plt.imshow(array)
    plt.show()

    cv2.imshow("Canvas", array)
    cv2.waitKey(0)
    #img = Image.fromarray(array, '1')
    #img.save('C:/Images/img.png')
    #img.show()


create_rand_image()