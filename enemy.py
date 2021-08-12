import random
from structs import Direction, Encodings


class Enemy:
    def __init__(self, enemy):
        self.enemy = enemy

    def action(self, state):
        (x, y) = self.enemy.head_indexes()
        max_x = len(state) - 1
        max_y = len(state[0]) - 1

        values = {Direction.UP: 0, Direction.DOWN: 0,
                  Direction.LEFT: 0, Direction.RIGHT: 0}

        if x < 1:
            values[Direction.LEFT] = 2
        elif state[x - 1][y] == Encodings.EMPTY.value:
            values[Direction.LEFT] = 0
        elif state[x - 1][y] == Encodings.PLAYER_HEAD.value:
            values[Direction.LEFT] = 1
        else:
            values[Direction.LEFT] = 2

        if x > max_x - 1:
            values[Direction.RIGHT] = 2
        elif state[x + 1][y] == Encodings.EMPTY.value:
            values[Direction.RIGHT] = 0
        elif state[x + 1][y] == Encodings.PLAYER_HEAD.value:
            values[Direction.RIGHT] = 1
        else:
            values[Direction.RIGHT] = 2

        if y < 1:
            values[Direction.UP] = 2
        elif state[x][y - 1] == Encodings.EMPTY.value:
            values[Direction.UP] = 0
        elif state[x][y - 1] == Encodings.PLAYER_HEAD.value:
            values[Direction.UP] = 1
        else:
            values[Direction.UP] = 2

        if y > max_y - 1:
            values[Direction.DOWN] = 2
        elif state[x][y + 1] == Encodings.EMPTY.value:
            values[Direction.DOWN] = 0
        elif state[x][y + 1] == Encodings.PLAYER_HEAD.value:
            values[Direction.DOWN] = 1
        else:
            values[Direction.DOWN] = 2

        min_value = min(values.values())

        best_actions = [
            direction for direction in values if values[direction] == min_value]

        return random.choice(best_actions)
