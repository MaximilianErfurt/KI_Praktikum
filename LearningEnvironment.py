import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy
from datetime import datetime
import tkinter
from tkinter import filedialog
from skimage.morphology import skeletonize

# import matplotlib.pyplot as plot
# from PIL import Image
# import os


# setting reward values
good_rotation_reward = 50
bad_rotation_reward = -50
neutral_rotation_reward = 0
local_goal_reached_with_center_reward = 150
local_goal_reached_reward = 75
local_goal_not_reached_reward = -25
out_of_bounds_reward = -100

collision_reward = -1000

# indexing parameters to check various things relating to state class and rewards
# goal reached indices
# they repeat for orientations 4 - 7
# orientation:                0 & 4             1 & 5             2 & 6                 3 & 7
goal_reached_indices = (((1, 2), (3, 2)), ((1, 3), (3, 1)), ((2, 1), (2, 3)), ((1, 1), (3, 3)))

# rotation collision detection indices
# cw rotations top, ccw rotations bot.:      0 & 4             1 & 5             2 & 6             3 & 7
rotation_collision_detected_indices = (((0, 1), (4, 3)), ((0, 3), (4, 1)), ((3, 0), (1, 4)), ((1, 0), (3, 4)),
                                       ((0, 3), (4, 1)), ((1, 4), (3, 0)), ((1, 0), (3, 4)), ((0, 1), (4, 3)))

# indices for contact positions:     0 & 4             1 & 5             2 & 6             3 & 7
contact_orientation_indices = (((0, 2), (4, 2)), ((0, 4), (4, 0)), ((2, 4), (2, 0)), ((4, 4), (0, 0)),
                               ((4, 2), (0, 2)), ((4, 0), (0, 4)), ((2, 0), (2, 4)), ((0, 0), (4, 4)))


def create_rand_image(mode):
    """
    Method to create images with random splines
    2 Modes:
    :param mode: 0 -> return as array, 1 -> save the global_environment in chosen folder
    :return: Array, if mode = 0
    """
    # global_environment
    x_size = 640
    y_size = 480
    array = np.zeros((y_size, x_size), dtype='uint8', )

    # generating random points
    x = np.arange(x_size / 12, x_size, x_size / 12, int)
    x_start = np.arange(0, int(x[0]), int(x[0]) / 3)
    x_end = np.arange(x[-1] + int(x[0]) / 3, x_size, int(x[0]) / 3)
    x = np.concatenate([x_start, x, x_end])
    y = np.random.randint(0 + int(0.2 * y_size), y_size - int(0.2 * y_size), len(x))
    print(len(y))

    # # fixing all spline points to test code
    # y[3] = 25 + 5
    # y[4] = 25 + 10
    # y[5] = 25 + 15
    # y[6] = 25 + 5
    # y[7] = 25 + 2
    # y[8] = 25 - 2
    # y[9] = 25 - 5
    # y[10] = 25 - 12
    # y[11] = 25 - 20
    # y[12] = 25
    # y[13] = 25
    # y[14] = 25

    # fix first and last three spline points to make it more realistic
    y[0] = y[1] = y[2] = y[-1] = y[-2] = y[-3] = y_size / 2

    # generate cubic spline
    spline = scipy.interpolate.CubicSpline(x=x, y=y)
    #
    # # plot the spline
    # xs = np.arange(0, x_size, 1)
    # fig, ax = plt.subplots(figsize=(6.5, 4))
    # ax.plot(x, y, 'o', label='data')
    # ax.plot(xs, spline(xs), label="S")
    # plt.show()

    # merge into array
    for i in range(x_size):
        array[int(spline(i)), i] = 255

    # fill up empty space
    kernel = np.ones((7, 7), np.uint8)
    array = cv2.dilate(array, kernel, iterations=1)

    # *255 is only needed if mode == 1 -> moved it into the if statement
    array = skeletonize(array)

    # loop to change all the values of the first 3 and last 3 columns to 0, as those sometimes turn out buggy
    for i in range(3):
        array[:, i] = array[:, - i - 1] = np.zeros(array.shape[0])
    array = skeletonize(array)

    # plot the graph
    # cv2.imshow("Canvas", array)
    # cv2.waitKey(0)

    # get folder and save
    if mode == 1:
        tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
        folder_path = filedialog.askdirectory()  # ask user for folder to save in

        # save array as global_environment
        curr_time = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        name = folder_path + "/Image" + curr_time + ".png"
        array = array * 255
        cv2.imwrite(name, array)  # imwrite(filename, img[, params])

    # return array
    if mode == 0:
        array_bool = np.zeros((array.shape[0], array.shape[1]), dtype=bool)
        # convert to bool for performance
        # numpy array conversion to bool doesn't work properly, so I'm doing it manually
        for i in range(array.shape[1]):
            for j in range(array.shape[0]):
                if not (array[j, i] == 0):
                    array_bool[j, i] = True
        return array_bool


def img_to_bool(bild: np.ndarray) -> np.ndarray:

    array_bool = np.zeros((bild.shape[0], bild.shape[1]), dtype=bool)
    # convert to bool for performance
    # numpy array conversion to bool doesn't work properly, so I'm doing it manually
    for i in range(bild.shape[1]):
        for j in range(bild.shape[0]):
            if not (bild[j, i] == 0):
                array_bool[j, i] = True
    return array_bool


def extract_path(array: np.ndarray) -> list[(int, int)]:
    """
    Takes a boolean array and returns a list of coordinates as (int, int) tuples, starting on the left side of the spline and ending on the right side
    :param array: Single-width boolean array of spline learning environment
    :return: List of coordinates
    """
    height = array.shape[0]
    width = array.shape[1]

    path = list()

    startpoint = (int, int)

    # loop to find the startpoint of spline
    # start iterating columns in top-left corner
    for i in range(width):
        startpoint_found = False
        # work your way through the rows -> j = row, i = column
        for j in range(height):
            if array[j, i]:
                # once part of the path has been found, check if it is truly the startpoint of the path. Do this by
                # checking all values in a 3x3 grid around the found point of the path. If only one is found,
                # it means the initially found point is the startpoint. This assumes column 0 will never have any true
                # values -> fix required if it does
                found_trues = 0
                for k in range(3):
                    for l in range(3):
                        # ignore the midpoint
                        if not (l == 1 and k == 1):
                            if array[j - 1 + l, i - 1 + k]:
                                found_trues += 1
                if found_trues == 1:
                    # value of 1 means startpoint has been found
                    startpoint_found = True
                    startpoint = (j, i)

                    # break out of row loop
                    break
        # break out of column loop if startpoint has been found
        if startpoint_found:
            break

    if startpoint == (0, 0):
        print("No Startpoint could be found! Returning empty list.")
        return path
    else:
        path.append(startpoint)

    # extract every element
    iteration = 0
    while True:
        new_point_found = False
        current_point = path[iteration]
        if not (iteration == 0):
            previous_point = path[iteration - 1]
        else:
            previous_point = (None, None)

        for i in range(3):
            for j in range(3):
                # ignore the midpoint
                if not (j == 1 and i == 1):
                    point_checked = (current_point[0] - 1 + j, current_point[1] - 1 + i)
                    # check if a point is found and, if yes, check that it isn't the point from the previous iteration
                    if array[point_checked[0], point_checked[1]] and not (point_checked == previous_point):
                        new_point_found = True
                        path.append(point_checked)
                        break
            if new_point_found:
                break

        # if no new point was found, break the while loop. List is now complete
        if not new_point_found:
            endpoint_found = True
            break

        iteration += 1

    if not endpoint_found:
        print("No spline endpoint could be found! Returning potentially incomplete path")
    return path


def determine_rotation_quality(local_environment: np.ndarray, orientation: int) -> int:
    """
    Determines if the angle of the contacts in relation to the wire is good/neutral/bad
    :param local_environment: Current local environment of the calling State object
    :param orientation: Current contact orientation
    :return: Reward value for the provided parameters
    """

    # First we simulate a rotation in either direction, check if a collision occurs and save the values as booleans
    rot_cw = not (determine_rotation_collision(local_environment, False, (orientation + 1) % 8) or determine_collision(
        local_environment, (orientation + 1) % 8))
    rot_ccw = not (determine_rotation_collision(local_environment, True, (orientation + 7) % 8) or determine_collision(
        local_environment, (orientation + 7) % 8))

    # check if both simulated rotations were possible. This means the contact was as centered as possible on the wire. If so, return good rotation reward
    if rot_ccw and rot_cw:
        return good_rotation_reward
    # check if only one value is True (rotation was only possible in one direction)
    elif rot_cw or rot_ccw and not (rot_cw and rot_ccw):
        # simulate another rotation in the direction that returned True
        if rot_cw:
            rot_cw_2 = not (determine_rotation_collision(local_environment, False, (orientation + 2) % 8)
                            or determine_collision(local_environment, (orientation + 2) % 8))
            # check if, in total, 0 rotations were possible in one direction and 2 in the other. If so, it means the contacts could have been more centered on the wire. Return bad rotation reward
            if rot_cw and rot_cw_2:
                return bad_rotation_reward
            else:
                return neutral_rotation_reward
        # do the same procedure for counter-clockwise rotation
        else:
            rot_ccw_2 = not (determine_rotation_collision(local_environment, True, (orientation + 6) % 8)
                             or determine_collision(local_environment, (orientation + 6) % 8))
            if rot_ccw and rot_ccw_2:
                return bad_rotation_reward
            else:
                return neutral_rotation_reward
    else:
        return neutral_rotation_reward


def determine_rotation_collision(local_environment: np.ndarray, rot_dir: bool, orientation: int) -> bool:
    """
    Determines if the previously performed rotation has caused a collision
    :param local_environment: 5 x 5 matrix of current environment
    :param rot_dir: Rotation that was performed (False = Clockwise, True = Counter-Clockwise)
    :param orientation: New
    :return: Collision detected boolean
    """

    # initialize return value
    collision = False

    # account for symmetry of orientations
    orientation %= 4
    if rot_dir:
        # check if it's a counter-clockwise rotation
        orientation += 4

    # save points to be checked  in attribute for readability
    checked_points = rotation_collision_detected_indices[orientation]

    for i in range(2):
        if local_environment[checked_points[i][0], checked_points[i][1]]:
            collision = True
            if collision:
                break

    return collision


def determine_collision(local_environment: np.ndarray, orientation: int) -> bool:
    """
    Determines if the current position of the contacts is the same position as a piece of the wire
    :param local_environment: Current local environment of calling State object
    :param orientation: Current contact orientation
    :return: Collision detected yes/no
    """

    # initialize return value
    collision = False

    # save points to be checked  in attribute for readability
    checked_points = contact_orientation_indices[orientation]

    for i in range(2):
        if local_environment[checked_points[i][0], checked_points[i][1]]:
            collision = True
            if collision:
                break

    return collision


class State:
    """
    Basic state class for our machine learning model
    """

    def __init__(self, global_environment: np.ndarray, goal_path: list[tuple[int, int]],
                 contact_position: tuple[int, int], contact_orientation: int, local_goal: int, previous_movement: int):
        """
        :param global_environment: The current global learning environment, as a rows x columns boolean array
        :param goal_path: The list of local goals in the learning environment, as returned by the :func:`extract_path()` function
        :param contact_position: Current midpoint position of the contacts, as a row x column coordinate tuple in the provided global_environment
        :param contact_orientation: Current orientation of the contacts, as a value of -1 - 7, starting at 0 with left contact at center top and right contact at center bottom, and rotating clockwise in 45° steps. A value of -1 will auto-detect the best possible starting orientation for the given wire (only makes sense with local_goal set to 1)
        :param local_goal: The current local goal, as an integer value indexing the provided goal_path list
        :param previous_movement: The movement that was made in order to get to this state. Necessary so the ML agent does not learn to move back and forth indefinitely.
        """
        self.local_goal = goal_path[local_goal]
        self.local_goal_val = local_goal
        self.current_goal_path = goal_path
        self.contact_position = contact_position
        self.local_environment = np.zeros((5, 5), dtype='uint8')
        self.previous_movement = previous_movement

        # Key for filling the local environment matrix:
        # 0 = empty space
        # 1 = wire
        for i in range(5):
            for j in range(5):
                if self.contact_position[0] - 2 + j < 0 or self.contact_position[1] - 2 + i < 0:
                    raise IndexError("Moved out of global environment boundaries!")
                self.local_environment[j, i] = int(
                    global_environment[self.contact_position[0] - 2 + j, self.contact_position[1] - 2 + i])

        if contact_orientation == -1:
            if self.local_environment[1, 2]:
                self.contact_orientation = 6
            elif self.local_environment[3, 2]:
                self.contact_orientation = 2
            elif self.local_environment[1, 3] or self.local_environment[2, 3] or self.local_environment[3, 3]:
                self.contact_orientation = 0
            else:
                self.contact_orientation = 4
        else:
            self.contact_orientation = contact_orientation

        if self.contact_orientation > 7 or self.contact_orientation < -1:
            raise ValueError("Invalid contact orientation provided! Use values from 0-7")

        self.hashcode = self.__hash__()

    def __repr__(self):
        """
        Reproduces the 5x5 local environment matrix and tries to add the local goal (2) as well as contacts (3), (4) to it.
        I do this because I do not want the local goal or contacts in the actual environment matrix, but I do want them printed
        """

        repr_matr = np.copy(self.local_environment)

        # Key for filling the local environment matrix:
        # 0 = empty space
        # 1 = wire
        # 2 = current local goal (if possible to add)
        # 3 = left contact
        # 4 = right contact
        try:
            repr_matr[self.local_goal[0] - self.contact_position[0] + 2, self.local_goal[1] - self.contact_position[
                1] + 2] = 2
        except IndexError:
            print("Local Goal outside of Local Environment!\n\n")

        # determine positioning of contacts from contact orientation value
        left_contact = contact_orientation_indices[self.contact_orientation][0]
        right_contact = contact_orientation_indices[self.contact_orientation][1]
        repr_matr[left_contact[0], left_contact[1]] = 3
        repr_matr[right_contact[0], right_contact[1]] = 4

        # I am aware that the following lines of code are a crime against humanity, but I won't be doing anything about it
        return "{}:\n\n{} {} {} {} {}\n{} {} {} {} {}\n{} {} {} {} {}\n{} {} {} {} {}\n{} {} {} {} {}\n\n".format(
            type(self).__name__, repr_matr[0, 0], repr_matr[0, 1], repr_matr[0, 2], repr_matr[0, 3], repr_matr[0, 4],
            repr_matr[1, 0], repr_matr[1, 1], repr_matr[1, 2], repr_matr[1, 3], repr_matr[1, 4], repr_matr[2, 0],
            repr_matr[2, 1], repr_matr[2, 2], repr_matr[2, 3], repr_matr[2, 4], repr_matr[3, 0], repr_matr[3, 1],
            repr_matr[3, 2], repr_matr[3, 3], repr_matr[3, 4], repr_matr[4, 0], repr_matr[4, 1], repr_matr[4, 2],
            repr_matr[4, 3], repr_matr[4, 4])

    def __hash__(self) -> int:
        """
        Takes local environment matrix and contact orientation and converts them into a unique value
        :return: binary hash, as integer value. Bits 0-24 are the local environment matrix, bits 25-27 are the contact orientation, bit 28 - 30 the previously made movement

        """

        # init hashcode
        hashcode = 0

        # convert environment to bytes
        environment_bytes = self.local_environment.tobytes()

        # fill each bit value, starting from the LSB
        for i in range(25):
            val = environment_bytes[- i - 1] << i
            hashcode += val

        # fill bits 25-27 with contact orientation value
        hashcode += self.contact_orientation << 25

        # fill bits 28-30 with the previously made movement value
        hashcode += self.previous_movement << 28

        return hashcode

    def set_next_local_goal(self) -> None:
        """
        Sets next local goal. Self-explanatory
        """
        if len(self.current_goal_path) > self.local_goal_val + 1 and self.local_goal_val > 0:
            self.local_goal_val += 1
            self.local_goal = self.current_goal_path[self.local_goal_val]
        else:
            # print("End of spline reached!")
            pass

    def movement(self, global_environment: np.ndarray, movement_type: int) -> ('State', int):
        match movement_type:
            case 0:
                return self.move_right(global_environment)
            case 1:
                return self.move_left(global_environment)
            case 2:
                return self.move_up(global_environment)
            case 3:
                return self.move_down(global_environment)
            case 4:
                return self.rotate_cw(global_environment)
            case 5:
                return self.rotate_ccw(global_environment)
            case _:
                raise ValueError("Invalid movement type!")

    def movement_reward(self, movement_type: int) -> int:
        """
        Determines the reward value for the movement that was performed. To be used in return values of State class movement methods. If a local goal was reached, it also set the new local goal for the calling State object
        :param movement_type: The Type of movement that was done. Values 0 - 3 are (in order) movement right, left, up, down. Values 4 & 5 are rotation clockwise & counter-clockwise
        :return: Reward value
        """

        # check if a collision occurred
        if determine_collision(self.local_environment, self.contact_orientation):
            return collision_reward

        # if a rotation was performed, check if this caused a collision on the way:
        if movement_type == 4:
            if determine_rotation_collision(self.local_environment, False, self.contact_orientation):
                return collision_reward
        elif movement_type == 5:
            if determine_rotation_collision(self.local_environment, True, self.contact_orientation):
                return collision_reward

        # init default reward value
        reward = local_goal_not_reached_reward
        local_goal_reached = False

        # % 4 because reached goal indices repeat
        checked_points = goal_reached_indices[self.contact_orientation % 4]

        # check if local goal is still in local environment
        local_goal_in_local_environment = (self.local_goal[0] - self.contact_position[0] + 2,
                                           self.local_goal[1] - self.contact_position[1] + 2)

        if max(local_goal_in_local_environment) > 4 or min(local_goal_in_local_environment) < 0:
            # this means the local goal moved out of the local environment
            return out_of_bounds_reward

        # if local goal is in bounds, check if it has been reached
        for i in range(2):
            if checked_points[i] == local_goal_in_local_environment:
                # this means the local goal has been reached, albeit not with the center point
                local_goal_reached = True
                if local_goal_reached:
                    reward = local_goal_reached_reward
                    break

        # check if local goal has been reached with center
        if local_goal_in_local_environment == (2, 2):
            local_goal_reached = True
            reward = local_goal_reached_with_center_reward

        # only if a translation was performed and goal was reached: check the quality of the contact's angle around the wire
        if movement_type < 4 and local_goal_reached:
            reward += determine_rotation_quality(self.local_environment, self.contact_orientation)

        # set next local goal if it has been reached
        if local_goal_reached:
            self.set_next_local_goal()

        # if nothing has been returned yet (no out of bounds, no collision), return calculated reward
        return reward

    def move_right(self, global_environment: np.ndarray) -> ('State', int):
        """
        Method that creates a new state object and returns a reward from a movement to the right in the provided global environment
        :param global_environment: The global environment in which the movement is to take place
        :return: Tuple in which value at index 0 is the new State object, and value at index 1 the reward resulting from the movement
        """
        new_contact_position = (self.contact_position[0], self.contact_position[1] + 1)
        new_state = State(global_environment, self.current_goal_path, new_contact_position, self.contact_orientation,
                          self.local_goal_val, 0)
        return new_state, new_state.movement_reward(0)

    def move_left(self, global_environment: np.ndarray) -> ('State', int):
        """
        Method that creates a new state object and returns a reward from a movement to the left in the provided global environment
        :param global_environment: The global environment in which the movement is to take place
        :return: Tuple in which value at index 0 is the new State object, and value at index 1 the reward resulting from the movement
        """
        new_contact_position = (self.contact_position[0], self.contact_position[1] - 1)
        new_state = State(global_environment, self.current_goal_path, new_contact_position, self.contact_orientation,
                          self.local_goal_val, 1)
        return new_state, new_state.movement_reward(1)

    def move_up(self, global_environment: np.ndarray) -> ('State', int):
        """
        Method that creates a new state object and returns a reward from a movement upwards in the provided global environment
        :param global_environment: The global environment in which the movement is to take place
        :return: Tuple in which value at index 0 is the new State object, and value at index 1 the reward resulting from the movement
        """
        new_contact_position = (self.contact_position[0] - 1, self.contact_position[1])
        new_state = State(global_environment, self.current_goal_path, new_contact_position, self.contact_orientation,
                          self.local_goal_val, 2)
        return new_state, new_state.movement_reward(2)

    def move_down(self, global_environment: np.ndarray) -> ('State', int):
        """
        Method that creates a new state object and returns a reward from a movement downwards in the provided global environment
        :param global_environment: The global environment in which the movement is to take place
        :return: Tuple in which value at index 0 is the new State object, and value at index 1 the reward resulting from the movement
        """
        new_contact_position = (self.contact_position[0] + 1, self.contact_position[1])
        new_state = State(global_environment, self.current_goal_path, new_contact_position, self.contact_orientation,
                          self.local_goal_val, 3)
        return new_state, new_state.movement_reward(3)

    def rotate_cw(self, global_environment: np.ndarray) -> ('State', int):
        """
        Method that creates a new state object and returns a reward from a clockwise rotation in the provided global environment
        :param global_environment: The global environment in which the movement is to take place
        :return: Tuple in which value at index 0 is the new State object, and value at index 1 the reward resulting from the movement
        """
        new_orientation = (self.contact_orientation + 1) % 8
        new_state = State(global_environment, self.current_goal_path, self.contact_position, new_orientation,
                          self.local_goal_val, 4)
        return new_state, new_state.movement_reward(4)

    def rotate_ccw(self, global_environment: np.ndarray) -> ('State', int):
        """
        Method that creates a new state object and returns a reward from a counter-clockwise rotation in the provided global environment
        :param global_environment: The global environment in which the movement is to take place
        :return: Tuple in which value at index 0 is the new State object, and value at index 1 the reward resulting from the movement
        """
        new_orientation = (self.contact_orientation + 7) % 8
        new_state = State(global_environment, self.current_goal_path, self.contact_position, new_orientation,
                          self.local_goal_val, 5)
        return new_state, new_state.movement_reward(5)
