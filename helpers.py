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


def get_grid(state, player_indexes, side_size):
    grid_state = []
    for i in range(side_size):
        grid_state.append([])
        for j in range(side_size):
            grid_state[i].append(Encodings.EMPTY.value)

    (board_x, board_y) = (len(state), len(state[0]))
    offset = int(-(side_size - 1) // 2)

    (x, y) = player_indexes

    offset_x = offset
    for i in range(side_size):
        actual_x = x + offset_x

        offset_y = offset
        for j in range(side_size):
            actual_y = y + offset_y
            if (actual_x < 0 or actual_x >= board_x or actual_y < 0 or actual_y >= board_y):
                grid_state[i][j] = Encodings.HIT.value
            else:
                grid_state[i][j] = state[actual_x][actual_y]
            offset_y += 1

        offset_x += 1

    return np.array(grid_state)


def flatten_grid(state, player_indexes, side_size):
    return get_grid(state, player_indexes, side_size).flatten()


def rotated_grid(state, player_indexes, side_size, direction):
    grid_state = get_grid(state, player_indexes, side_size)

    if direction == Direction.LEFT:
        grid_state = np.rot90(grid_state, k=1)
    elif direction == Direction.RIGHT:
        grid_state = np.rot90(grid_state, k=-1)
    elif direction == Direction.DOWN:
        grid_state = np.rot90(grid_state, k=2)

    return grid_state.flatten()


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

    return action
