import cv2
import numpy as np

import LearningEnvironment as Le
import Bildverarbeitung as Bv
import QTable

generated_spline = Le.create_rand_image(0)
print(generated_spline)
path = Le.extract_path(generated_spline)
print(Le.extract_path.__doc__)

# create test Object from State class
test_state = Le.State(generated_spline, path, path[0], 0, 1)
print(test_state)


# img = cv2.imread('Draht.jpeg')
# Bv.reduce_Draht_to_Line(draht=img)

qtable = QTable.new_q_table()
# training goes here


np.save('qtable.npy', qtable)
