import numpy as np
import tensorflow as tf
from structs import Direction


ROTATING_ACTIONS = {Direction.UP: [0, 1, 2, 3], Direction.LEFT: [3, 2, 0, 1],
                    Direction.DOWN: [1, 0, 3, 2], Direction.RIGHT: [2, 3, 1, 0]}


def as_indexes(position, block_size):
    return (int(position[0] // block_size), int(position[1] // block_size))


def disassemble(batch):
    (states, actions, rewards, next_states) = ([], [], [], [])

    for experience in batch:
        states.append(experience[0])
        actions.append(experience[1])
        rewards.append(experience[2])
        next_states.append(experience[3])

    return (tf.convert_to_tensor(np.array(states)), tf.convert_to_tensor(np.array(actions)), tf.convert_to_tensor(np.array(rewards), dtype=tf.float32), tf.convert_to_tensor(np.array(next_states)))


def best_possible_action(actions, direction, rotated=False):
    arg_sorted = tf.argsort(actions[0])

    if rotated:
        rot_direction = direction
    else:
        rot_direction = Direction.UP

    up = ROTATING_ACTIONS[rot_direction][0]
    down = ROTATING_ACTIONS[rot_direction][1]
    left = ROTATING_ACTIONS[rot_direction][2]
    right = ROTATING_ACTIONS[rot_direction][3]

    if direction == Direction.UP:
        action = arg_sorted[arg_sorted != down][2]
    elif direction == Direction.DOWN:
        action = arg_sorted[arg_sorted != up][2]
    elif direction == Direction.LEFT:
        action = arg_sorted[arg_sorted != right][2]
    elif direction == Direction.RIGHT:
        action = arg_sorted[arg_sorted != left][2]

    return action.numpy()
