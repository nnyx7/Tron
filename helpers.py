import numpy as np


def as_indexes(position, block_size):
    return (int(position[0] // block_size), int(position[1] // block_size))


def flatten(state, board_size):
    flatten_state = []
    for i in range(board_size[0]):
        for j in range(board_size[1]):
            flatten_state.append(state[i][j])
    return flatten_state


def disassemble(batch):
    (states, actions, rewards, next_states) = ([], [], [], [])

    for experience in batch:
        states.append(experience[0])
        actions.append(experience[1])
        rewards.append(experience[2])
        next_states.append(experience[3])

    return (np.array(states), np.array(actions), np.array(rewards), np.array(next_states))
