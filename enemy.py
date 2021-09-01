import random
from structs import Direction


def get_best_actions(state, pos, max_x, max_y, encodings):
    (x, y) = pos

    values = {Direction.UP: 0, Direction.DOWN: 0,
              Direction.LEFT: 0, Direction.RIGHT: 0}

    # left
    if x >= 1 and state[x - 1][y] == encodings.EMPTY.value:
        values[Direction.LEFT] = 0
    else:
        values[Direction.LEFT] = 2

    # right
    if x <= (max_x - 1) and state[x + 1][y] == encodings.EMPTY.value:
        values[Direction.RIGHT] = 0
    else:
        values[Direction.RIGHT] = 2

    # up
    if y >= 1 and state[x][y - 1] == encodings.EMPTY.value:
        values[Direction.UP] = 0
    else:
        values[Direction.UP] = 2

    # down
    if y <= (max_y - 1) and state[x][y + 1] == encodings.EMPTY.value:
        values[Direction.DOWN] = 0
    else:
        values[Direction.DOWN] = 2

    min_value = min(values.values())

    best_actions = [
        direction for direction in values if values[direction] == min_value]

    return best_actions


def can_move_same_direction(state, pos, max_x, max_y, direction, encodings):
    (x, y) = pos

    can_move = False
    if direction == Direction.LEFT:
        if x - 1 >= 0 and state[x-1][y] == encodings.EMPTY.value:
            can_move = True
    elif direction == Direction.RIGHT:
        if x + 1 < max_x and state[x+1][y] == encodings.EMPTY.value:
            can_move = True
    elif direction == Direction.UP:
        if y - 1 >= 0 and state[x][y-1] == encodings.EMPTY.value:
            can_move = True
    elif direction == Direction.DOWN:
        if y + 1 < max_y and state[x][y+1] == encodings.EMPTY.value:
            can_move = True
    return can_move


class Enemy:
    def __init__(self, enemy, encodings):
        self.enemy = enemy
        self.encodings = encodings

    def __call__(self, state):
        return self.action(state)

    def action(self, state):
        pos = self.enemy.head_indexes()
        max_x = len(state) - 1
        max_y = len(state[0]) - 1

        best_actions = get_best_actions(
            state, pos, max_x, max_y, self.encodings)
        return random.choice(best_actions)


class SmarterEnemy:
    def __init__(self, enemy, encodings):
        self.enemy = enemy
        self.encodings = encodings

    def __call__(self, state):
        return self.action(state)

    def action(self, state):
        pos = self.enemy.head_indexes()
        max_x = len(state) - 1
        max_y = len(state[0]) - 1

        if can_move_same_direction(state, pos, max_x, max_y,
                                   self.enemy.direction, self.encodings):
            action = self.enemy.direction
        else:
            best_actions = get_best_actions(
                state, pos, max_x, max_y, self.encodings)
            action = random.choice(best_actions)

        return action
