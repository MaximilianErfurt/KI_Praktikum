import cv2
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image



def create_rand_image():
    array = np.zeros((400, 400), dtype=int, )
    print(array)
    image = Image.fromarray(array, "1")
    image.show()

create_rand_image()