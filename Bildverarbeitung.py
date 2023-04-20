import cv2
import numpy as np
from skimage.morphology import skeletonize
from skimage import data
import matplotlib.pyplot as plt
from skimage.util import invert
import numpy
from sklearn.metrics import r2_score

def reduce_Draht_to_Line(draht):

    # original image to grey image
    img_gray = cv2.cvtColor(draht, cv2.COLOR_BGR2GRAY)

    # blur image for better edge detection with median blur
    img_blur = cv2.medianBlur(img_gray, 15)

    # Canny edge detection
    edges = cv2.Canny(image=img_blur, threshold1=0, threshold2=200)  # Canny Edge Detection

    # reducing the two edges to one centered line
    kernel = np.ones((7, 7), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=10)
    skeleton = skeletonize(edges)

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4),
                             sharex=True, sharey=True)


    # ploting the picture
    ax = axes.ravel()
    ax[0].imshow(edges, cmap=plt.cm.gray)
    ax[0].axis('off')
    ax[0].set_title('original', fontsize=20)
    ax[1].imshow(skeleton, cmap=plt.cm.gray)
    ax[1].axis('off')
    ax[1].set_title('skeleton', fontsize=20)
    fig.tight_layout()
    plt.show()
    cv2.destroyAllWindows()