import numpy as np

import LearningEnvironment
import LearningEnvironment as Le
import random
import copy


def new_q_table() -> dict:
    return {}


def train_wire(environment: np.ndarray, path: list[(int, int)], qtable: dict, iterations: int, gamma: float,
               alpha: float, epsilon: float) -> dict:
    n_goals = len(path)
    current_local_goal = 1

    for i in range(iterations):
        print("Iteration: {}\n".format(i + 1))
        checkpoint = copy.deepcopy((path[0], -1, 1, 0))
        current_state = Le.State(global_environment=environment, goal_path=path, contact_position=checkpoint[0],
                                 contact_orientation=checkpoint[1], local_goal=checkpoint[2],
                                 previous_movement=checkpoint[3])
        while current_local_goal < n_goals:
            current_hash = current_state.hashcode
            current_state_exists = current_hash in qtable

            # set new checkpoint every 10 local goals
            if (not (current_local_goal == 1)) and (current_local_goal % 10) == 1:
                checkpoint = copy.deepcopy((current_state.contact_position, current_state.contact_orientation,
                                            current_local_goal, current_state.previous_movement))

            # fetch old q values
            if not current_state_exists:
                q_old_vals = np.zeros((6, 1))
                qtable[current_hash] = copy.deepcopy(q_old_vals)
            else:
                q_old_vals = copy.deepcopy(qtable[current_hash])

            for action in range(6):
                # iterate through every action for your current state
                # determine updated q-value for every action

                # if at the left end of spline and movement type is 4 or 5 (rotate cw, ccw), skip this action
                # if ((action == 4) or (action == 5)) and current_state.contact_position[1] <= 4:
                #     continue
                #
                # # if at the right end of spline and movement type is 4 or 5 (rotate cw, ccw), skip this action
                # if ((action == 4) or (action == 5)) and current_state.contact_position[1] >= (
                #         environment.shape[1] - 5):
                #     continue

                try:
                    (new_state, new_reward) = current_state.movement(environment, action)
                    # print("Movement: {}\nReward:{}\n\n".format(action, new_reward))
                    new_hash = new_state.hashcode
                    new_state_exists = new_hash in qtable

                    # determine future reward
                    if new_state_exists:
                        # pick maximum reward of future state
                        future_reward = np.max(qtable[new_hash])
                    else:
                        # or pick 0, if future state doesn't exist yet
                        future_reward = 0

                    # Bellmann equation
                    new_q_val = (1 - alpha) * q_old_vals[action] + alpha * (new_reward + gamma * future_reward)
                    qtable[current_hash][action] = new_q_val
                except IndexError:
                    # this means the contacts moved out of bounds
                    new_reward = LearningEnvironment.out_of_bounds_reward
                    new_q_val = (1 - alpha) * q_old_vals[action] + alpha * new_reward
                    qtable[current_hash][action] = new_q_val
                    continue

            q_new_vals = copy.deepcopy(qtable[current_hash])

            # pick the action with the highest reward, or pick a random action (determined by epsilon)
            if random.random() <= epsilon:
                action = np.argmax(q_new_vals)
            else:
                action = random.randrange(6)

            # # if at the left end of spline and movement type is 1, 4 or 5 (move left, rotate cw, ccw) -> pick another movement
            # if ((action == 1) or (action == 4) or (action == 5)) and current_state.contact_position[1] <= 4:
            #     new_rand = random.randrange(3)
            #     action = new_rand
            #     if not (action == 0):
            #         action += 1

            # # if at the right end of spline and movement type is 0, 4 or 5 (move right, rotate cw, ccw) -> pick another movement
            # if ((action == 0) or (action == 4) or (action == 5)) and current_state.contact_position[1] >= (
            #         environment.shape[1] - 5):
            #     new_rand = random.randrange(3)
            #     action = new_rand + 1

            # no q-value updates this time
            try:
                (new_state, new_reward) = current_state.movement(environment, action)

            except IndexError:
                # this means the contacts moved out of bounds -> reset to checkpoint
                current_state = Le.State(global_environment=environment, goal_path=path,
                                         contact_position=checkpoint[0],
                                         contact_orientation=checkpoint[1], local_goal=checkpoint[2],
                                         previous_movement=checkpoint[3])
                current_local_goal = checkpoint[2]
                continue

            # Check if a collision occurred
            if new_reward <= LearningEnvironment.collision_reward:
                # If a collision occurred, reset to the checkpoint
                current_state = Le.State(global_environment=environment, goal_path=path,
                                         contact_position=checkpoint[0],
                                         contact_orientation=checkpoint[1], local_goal=checkpoint[2],
                                         previous_movement=checkpoint[3])
                current_local_goal = checkpoint[2]
            else:
                # If no collision occurred, set new local goal parameter
                # if new_state.local_goal_val > current_local_goal:
                #     print("New local goal: {}\n".format(new_state.local_goal_val))
                current_local_goal = new_state.local_goal_val

                # If final local goal is active and last reward was high, it means the path is completed
                # If that is the case, iterate the local goal parameter once more to break the while loop
                if (new_state.local_goal_val + 1) == n_goals and new_reward > 25:
                    current_local_goal += 1

                # set new state as current state
                current_state = new_state
        # reset local goal
        current_local_goal = 1

    path_reversed = copy.deepcopy(path)
    path_reversed.reverse()

    for i in range(iterations):
        print("Iteration: {}\n".format(i + 1))
        checkpoint = copy.deepcopy((path_reversed[0], -1, 1, 1))
        current_state = Le.State(global_environment=environment, goal_path=path_reversed,
                                 contact_position=checkpoint[0],
                                 contact_orientation=checkpoint[1], local_goal=checkpoint[2],
                                 previous_movement=checkpoint[3])
        while current_local_goal < n_goals:
            current_hash = current_state.hashcode
            current_state_exists = current_hash in qtable

            # set new checkpoint every 10 local goals
            if (not (current_local_goal == 1)) and (current_local_goal % 10) == 1:
                checkpoint = copy.deepcopy((current_state.contact_position, current_state.contact_orientation,
                                            current_local_goal, current_state.previous_movement))

            # fetch old q values
            if not current_state_exists:
                q_old_vals = np.zeros((6, 1))
                qtable[current_hash] = copy.deepcopy(q_old_vals)
            else:
                q_old_vals = copy.deepcopy(qtable[current_hash])

            for action in range(6):
                # iterate through every action for your current state
                # determine updated q-value for every action

                # if at the left end of spline and movement type is 1, 4 or 5 (move left, rotate cw, ccw), skip this action
                # if ((action == 1) or (action == 4) or (action == 5)) and current_state.contact_position[1] <= 4:
                #     continue
                #
                # # if at the right end of spline and movement type is 0, 4 or 5 (move right, rotate cw, ccw), skip this action
                # if ((action == 0) or (action == 4) or (action == 5)) and current_state.contact_position[1] >= (
                #         environment.shape[1] - 5):
                #     continue

                try:
                    (new_state, new_reward) = current_state.movement(environment, action)
                    # print("Movement: {}\nReward:{}\n\n".format(action, new_reward))
                    new_hash = new_state.hashcode
                    new_state_exists = new_hash in qtable

                    # determine future reward
                    if new_state_exists:
                        # pick maximum reward of future state
                        future_reward = np.max(qtable[new_hash])
                    else:
                        # or pick 0, if future state doesn't exist yet
                        future_reward = 0

                    # Bellmann equation
                    new_q_val = (1 - alpha) * q_old_vals[action] + alpha * (new_reward + gamma * future_reward)
                    qtable[current_hash][action] = new_q_val
                except IndexError:
                    # this means the contacts moved out of bounds
                    new_reward = LearningEnvironment.out_of_bounds_reward
                    new_q_val = (1 - alpha) * q_old_vals[action] + alpha * new_reward
                    qtable[current_hash][action] = new_q_val
                    continue

            q_new_vals = copy.deepcopy(qtable[current_hash])

            # pick the action with the highest reward, or pick a random action (determined by epsilon)
            if random.random() <= epsilon:
                action = np.argmax(q_new_vals)
            else:
                action = random.randrange(6)

            # # if at the left end of spline and movement type is 1, 4 or 5 (move left, rotate cw, ccw) -> pick another movement
            # if ((action == 1) or (action == 4) or (action == 5)) and current_state.contact_position[1] <= 4:
            #     new_rand = random.randrange(3)
            #     action = new_rand
            #     if not (action == 0):
            #         action += 1

            # # if at the right end of spline and movement type is 0, 4 or 5 (move right, rotate cw, ccw) -> pick another movement
            # if ((action == 0) or (action == 4) or (action == 5)) and current_state.contact_position[1] >= (
            #         environment.shape[1] - 5):
            #     new_rand = random.randrange(3)
            #     action = new_rand + 1

            # no q-value updates this time
            try:
                (new_state, new_reward) = current_state.movement(environment, action)

            except IndexError:
                # this means the contacts moved out of bounds -> reset to checkpoint
                current_state = Le.State(global_environment=environment, goal_path=path_reversed,
                                         contact_position=checkpoint[0],
                                         contact_orientation=checkpoint[1], local_goal=checkpoint[2],
                                         previous_movement=checkpoint[3])
                current_local_goal = checkpoint[2]
                continue

            # Check if a collision occurred
            if new_reward <= LearningEnvironment.collision_reward:
                # If a collision occurred, reset to the checkpoint
                current_state = Le.State(global_environment=environment, goal_path=path_reversed,
                                         contact_position=checkpoint[0],
                                         contact_orientation=checkpoint[1], local_goal=checkpoint[2],
                                         previous_movement=checkpoint[3])
                current_local_goal = checkpoint[2]
            else:
                # If no collision occurred, set new local goal parameter
                # if new_state.local_goal_val > current_local_goal:
                #     print("New local goal: {}\n".format(new_state.local_goal_val))
                current_local_goal = new_state.local_goal_val

                # If final local goal is active and last reward was high, it means the path is completed
                # If that is the case, iterate the local goal parameter once more to break the while loop
                if (new_state.local_goal_val + 1) == n_goals and new_reward > 25:
                    current_local_goal += 1

                # set new state as current state
                current_state = new_state

        # reset local goal
        current_local_goal = 1
    # after all iterations have been run through, return the q-table
    return qtable


def optimal_path(environment: np.ndarray, path: list[(int, int)], qtable: dict) -> list:
    n_goals = len(path)
    current_local_goal = 1

    movements = list()

    current_state = Le.State(global_environment=environment, goal_path=path, contact_position=path[0],
                             contact_orientation=-1, local_goal=current_local_goal, previous_movement=0)
    while current_local_goal < n_goals:
        current_hash = current_state.hashcode
        current_state_exists = current_hash in qtable

        # fetch q values
        if current_state_exists:
            q_vals = qtable[current_hash]
        # or generate new ones (ideally, in a well-trained model, this shouldn't happen)
        else:
            q_vals = np.zeros((6, 1))

        # pick the action with the highest reward, or pick a random action if it doesn't exist
        if current_state_exists:
            action = np.argmax(q_vals)
        else:
            action = random.randrange(6)

        # # if at the left end of spline and movement type is 1, 4 or 5 (move left, rotate cw, ccw) -> pick another movement
        # if ((action == 1) or (action == 4) or (action == 5)) and current_state.contact_position[1] <= 4:
        #     new_rand = random.randrange(3)
        #     action = new_rand
        #     if not (action == 0):
        #         action += 1

        # # if at the right end of spline and movement type is 0, 4 or 5 (move right, rotate cw, ccw) -> pick another movement
        # if ((action == 0) or (action == 4) or (action == 5)) and current_state.contact_position[1] >= (
        #         environment.shape[1] - 5):
        #     new_rand = random.randrange(3)
        #     action = new_rand + 1

        # action has now been determined -> generate new state
        try:
            (new_state, reward) = current_state.movement(environment, action)
            # print("Movement: {}\nReward:{}\n\n".format(action, new_reward))

        except IndexError:
            # this means the contacts moved out of bounds -> throw error
            raise IndexError("Moved out of bounds! More training required!")

        # Check if a collision occurred
        if reward <= LearningEnvironment.collision_reward:
            # If a collision occurred, throw error
            raise IndexError("Collided! More training required!")
        else:
            # If no collision occurred, set new local goal parameter
            # if new_state.local_goal_val > current_local_goal:
            #     print("New local goal: {}\n".format(new_state.local_goal_val))
            current_local_goal = new_state.local_goal_val

            # If final local goal is active and last reward was high, it means the path is completed
            # If that is the case, iterate the local goal parameter once more to break the while loop
            if (new_state.local_goal_val + 1) == n_goals and reward > 50:
                current_local_goal += 1

            # set new state as current state

            movements.append((current_state.__repr__(), action, current_hash))
            current_state = new_state

    return movements
