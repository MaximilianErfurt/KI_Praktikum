import cv2
import numpy as np

import LearningEnvironment as Le
import Bildverarbeitung as Bv
import QTable

generated_spline = Le.create_rand_image(0)
path = Le.extract_path(generated_spline)

# create test Object from State class
test_state = Le.State(generated_spline, path, path[0], -1, 1)
new_state = test_state.move_left(generated_spline)


# img = cv2.imread('Draht.jpeg')
# Bv.reduce_Draht_to_Line(draht=img)

try:
    qtable = np.load('qtable.npy', allow_pickle=True).item()
except FileNotFoundError:
    qtable = {}

qtable = QTable.train_wire(generated_spline, path, qtable, 100, 0.9, 0.3, 0.9)

# print(len(path))

np.save('qtable.npy', qtable)

