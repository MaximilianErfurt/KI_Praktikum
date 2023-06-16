import cv2
import numpy as np

import LearningEnvironment as Le
import Bildverarbeitung as Bv
import QTable
import Visualisierung as vi
import XMLVerarbeitung as Xv
import HotWire_Srv as Hws
from datetime import datetime
import threading


# create test Object from State class
# test_state = Le.State(generated_spline, path, path[0], -1, 1, 0)
# new_state = test_state.move_left(generated_spline)

server_thread = threading.Thread(target=Hws.server)
server_thread.start()

Hws.ai_state = 0

# press space to take photo
cv2.namedWindow("img", cv2.WINDOW_NORMAL)
cv2.resizeWindow("img", 1280, 960)

cv2.waitKey(0)


camera = cv2.VideoCapture(1)
return_value, image = camera.read()
curr_time = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
cv2.imwrite('./images/RobotPOV.png', image)
del camera


# calculate movement path
img = cv2.imread('./images/RobotPOV.png')
img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
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

    qtable = QTable.train_wire(generated_spline, path, qtable, 20, 0.8, 0.3, 0.9)

    # qtable_sorted = dict(sorted(qtable.items()))

    np.save('qtable.npy', qtable)

try:
    qtable = np.load('qtable.npy', allow_pickle=True).item()
except FileNotFoundError:
    qtable = {}

open('movements.txt', 'w').close()
movements = QTable.optimal_path(generated_spline, path, qtable)

movementstring = "ddddddd"
for entry in movements:
    match entry[1]:
        case 0:
            movementstring += "r"
        case 1:
            movementstring += "l"
        case 2:
            movementstring += "u"
        case 3:
            movementstring += "d"
        case 4:
            movementstring += "c"
        case 5:
            movementstring += "w"
        case _:
            raise ValueError

line = Bv.back_to_rgb(generated_spline)
cv2.imshow("img", line)
cv2.waitKey(0)

f = open('movements.txt', 'w')
f.write(movementstring)

r = Xv.compress_split_string(movementstring)

seq = ""
i = 0

for entry in r:
    seq += Hws.make_seq_s(i, entry)
    i += 1

conf = Hws.make_config(1.39, 1.0)

Hws.ai_sequence = seq
Hws.ai_config = conf

Hws.ai_state = 2

f.close()

vi.visualise(line, movementstring, x_start=movements[0][0][0], y_start=movements[0][0][1], movements=movements)
