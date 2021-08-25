import random

from constants import ACTIONS, BLOCK_SIZE
from helpers import as_indexes
from structs import Direction


class Player:
    def __init__(self, x_index_limits, y_index_limits, board_size):
        self.x_index_limits = x_index_limits
        self.y_index_limits = y_index_limits
        self.board_size = board_size

        self.reset()

    def reset(self, init_pos=None):
        self.length = 1
        if init_pos:
            self.x = [init_pos[0]]
            self.y = [init_pos[1]]
        else:
            (x_min, x_max) = self.x_index_limits
            (y_min, y_max) = self.y_index_limits
            self.x = [random.randrange(x_min, x_max) * 30]
            self.y = [random.randrange(y_min, y_max) * 30]

        self.direction = random.choice(ACTIONS)

    def move(self, action, first_move):
        if first_move:
            if (action == Direction.UP or action == Direction.DOWN
                    or action == Direction.LEFT or action == Direction.RIGHT):
                self.direction = action
        else:
            if action == Direction.UP and \
                    self.direction != Direction.DOWN:
                self.direction = Direction.UP

            elif action == Direction.DOWN and \
                    self.direction != Direction.UP:
                self.direction = Direction.DOWN

            elif action == Direction.LEFT and \
                    self.direction != Direction.RIGHT:
                self.direction = Direction.LEFT

            elif action == Direction.RIGHT and \
                    self.direction != Direction.LEFT:
                self.direction = Direction.RIGHT

    def progress(self):
        (last_x, last_y) = self.head()

        if self.direction == Direction.UP:
            self.x.append(last_x)
            self.y.append(last_y - BLOCK_SIZE)
        if self.direction == Direction.DOWN:
            self.x.append(last_x)
            self.y.append(last_y + BLOCK_SIZE)
        if self.direction == Direction.LEFT:
            self.x.append(last_x - BLOCK_SIZE)
            self.y.append(last_y)
        if self.direction == Direction.RIGHT:
            self.x.append(last_x + BLOCK_SIZE)
            self.y.append(last_y)

        self.length += 1

    def head(self):
        return (self.x[self.length - 1], self.y[self.length - 1])

    def head_indexes(self):
        return as_indexes(self.head(), BLOCK_SIZE)

    def prev_head(self):
        prev_index = self.length - 2
        return (self.x[prev_index], self.y[prev_index])

    def prev_head_indexes(self):
        return as_indexes(self.prev_head(), BLOCK_SIZE)

    def collision_with_wall(self):
        (head_x, head_y) = self.head()
        (screen_x, screen_y) = self.board_size
        return (head_x < 0 or head_x > (
            screen_x - BLOCK_SIZE) or head_y < 0 or head_y > (screen_y - BLOCK_SIZE))

    def collision(self, enemy_positions):
        (head_x, head_y) = self.head()

        crashing_in_enemy = False
        if enemy_positions:
            (enemy_x, enemy_y) = enemy_positions
            for i in range(len(enemy_x)):
                if ((head_x, head_y) == (enemy_x[i], enemy_y[i])):
                    crashing_in_enemy = True
                    break

        crashing_in_self = False
        for i in range(len(self.x) - 1):
            if ((head_x, head_y) == (self.x[i], self.y[i])):
                crashing_in_self = True
                break

        return (self.collision_with_wall() or crashing_in_enemy or crashing_in_self)
