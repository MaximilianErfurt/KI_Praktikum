import cv2

import LearningEnvironment as le
import Bildverarbeitung as bv


img = cv2.imread('Draht.jpeg')
bv.reduce_Draht_to_Line(draht=img)


