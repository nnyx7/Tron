import numpy as np

from structs import Encodings


def as_indexes(position, block_size):
    return (int(position[0] // block_size), int(position[1] // block_size))


# def flatten(state, board_size):
#     flatten_state = []
#     for i in range(board_size[0]):
#         for j in range(board_size[1]):
#           flatten_state.append(state[i][j])
#     return flatten_state


def disassemble(batch):
    (states, actions, rewards, next_states) = ([], [], [], [])

    for experience in batch:
        states.append(experience[0])
        actions.append(experience[1])
        rewards.append(experience[2])
        next_states.append(experience[3])

    return (np.array(states), np.array(actions), np.array(rewards), np.array(next_states))


def flatten_grid(state, player_indexes, side_size):
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
                grid_state[i][j] = Encodings.WALL_HIT.value
            else:
                grid_state[i][j] = state[actual_x][actual_y]
            offset_y += 1

        offset_x += 1

    return np.array(grid_state).flatten()
