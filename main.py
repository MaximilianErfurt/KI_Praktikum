import cv2

import LearningEnvironment as Le
import Bildverarbeitung as Bv

generated_spline = Le.create_rand_image(0)
path = Le.extract_path(generated_spline)

# create test Object from State class
test_state = Le.State(generated_spline, path, path[0], 0, 1)
print(test_state)

# img = cv2.imread('Draht.jpeg')
# Bv.reduce_Draht_to_Line(draht=img)


