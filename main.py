import cv2
import numpy as np

import LearningEnvironment as Le
import Bildverarbeitung as Bv
import QTable


# create test Object from State class
# test_state = Le.State(generated_spline, path, path[0], -1, 1, 0)
# new_state = test_state.move_left(generated_spline)


# img = cv2.imread('Draht.jpeg')
# Bv.reduce_Draht_to_Line(draht=img)

generated_spline = Le.create_rand_image(0)
path = Le.extract_path(generated_spline)

for i in range(50):
    generated_spline = Le.create_rand_image(0)
    path = Le.extract_path(generated_spline)
    print("Iteration: {}\n".format(i+1))
    try:
        qtable = np.load('qtable.npy', allow_pickle=True).item()
    except FileNotFoundError:
        qtable = {}

    qtable = QTable.train_wire(generated_spline, path, qtable, 100, 0.8, 0.3, 0.9)

    # qtable_sorted = dict(sorted(qtable.items()))

    np.save('qtable.npy', qtable)

try:
    qtable = np.load('qtable.npy', allow_pickle=True).item()
except FileNotFoundError:
    qtable = {}

movements = QTable.optimal_path(generated_spline, path, qtable)
f = open('movements.txt', 'w')

for entry in movements:
    f.write("Hash: {}\n{}\nAction: {}\n\n".format(entry[2], entry[0], entry[1]))
