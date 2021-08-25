import numpy as np
import tensorflow as tf
from structs import Direction, Encodings


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


def best_possible_action(actions, direction):
    arg_sorted = tf.argsort(actions[0])

    if direction == Direction.UP:
        action = arg_sorted[arg_sorted != 1][2]
    elif direction == Direction.DOWN:
        action = arg_sorted[arg_sorted != 0][2]
    elif direction == Direction.LEFT:
        action = arg_sorted[arg_sorted != 3][2]
    elif direction == Direction.RIGHT:
        action = arg_sorted[arg_sorted != 2][2]

    return action.numpy()
