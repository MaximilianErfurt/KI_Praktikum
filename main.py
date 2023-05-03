import cv2

import LearningEnvironment as Le
import Bildverarbeitung as Bv

generated_spline = Le.create_rand_image(0)
print(generated_spline)
path = Le.extract_path(generated_spline)
print(Le.extract_path.__doc__)

# create test Object from State class
test_state = Le.State(generated_spline, path, path[0], 0, 1)
print(test_state)

# test_movement_up = test_state.move_up(generated_spline)
# print("{}\nReward for this movement: {}\n".format(test_movement_up[0], test_movement_up[1]))

test_movement_right = test_state.move_right(generated_spline)
print("{}\nReward for this movement: {}\n".format(test_movement_right[0], test_movement_right[1]))

test_movement_cw = test_movement_right[0].rotate_cw(generated_spline)[0].rotate_cw(generated_spline)[0].rotate_cw(generated_spline)
print("{}\nReward for this movement: {}\n".format(test_movement_cw[0], test_movement_cw[1]))

# img = cv2.imread('Draht.jpeg')
# Bv.reduce_Draht_to_Line(draht=img)


