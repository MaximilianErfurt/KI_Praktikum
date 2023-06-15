import cv2
import numpy as np

import LearningEnvironment as Le
import Bildverarbeitung as Bv
import QTable
import Visualisierung as vi


# create test Object from State class
# test_state = Le.State(generated_spline, path, path[0], -1, 1, 0)
# new_state = test_state.move_left(generated_spline)


img = cv2.imread('./images/2023-06-05_12_48_29.jpeg')
cv2.imshow("img", img)
cv2.waitKey(0)
cv2.destroyWindow("img")

line = Bv.reduce_draht_to_line(draht=img)
line_cropped = Bv.crop_and_flip_image(line, 4)
generated_spline = Le.img_to_bool(line_cropped)
path = Le.extract_path(generated_spline)

for i in range(1):
    # generated_spline = Le.create_rand_image(0)
    # path = Le.extract_path(generated_spline)
    print("Iteration: {}\n".format(i+1))
    try:
        qtable = np.load('qtable.npy', allow_pickle=True).item()
    except FileNotFoundError:
        qtable = {}

    qtable = QTable.train_wire(generated_spline, path, qtable, 10, 0.8, 0.3, 0.9)

    # qtable_sorted = dict(sorted(qtable.items()))

    np.save('qtable.npy', qtable)

try:
    qtable = np.load('qtable.npy', allow_pickle=True).item()
except FileNotFoundError:
    qtable = {}

movements = QTable.optimal_path(generated_spline, path, qtable)
f = open('movements.txt', 'w')

movement = ""
for entry in movements:
    match entry[1]:
        case 0:
            movement += "r"
        case 1:
            movement += "l"
        case 2:
            movement += "u"
        case 3:
            movement += "d"
        case 4:
            movement += "c"
        case 5:
            movement += "w"
        case _:
            raise ValueError

line = Bv.back_to_rgb(generated_spline)
cv2.imshow("img", line)
cv2.waitKey(0)

f.write(movement)

vi.visualise(line, movement, x_start=movements[0][0][0], y_start=movements[0][0][1], movements=movements)