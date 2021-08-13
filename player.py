from constants import BLOCK_SIZE
from helpers import as_indexes
from structs import Direction


class Player:
    def __init__(self, init_coordinates, board_size):
        self.init_coordinates = init_coordinates
        self.board_size = board_size

        self.reset()

    def reset(self):
        self.length = 1
        self.x = [self.init_coordinates[0]]
        self.y = [self.init_coordinates[1]]
        self.direction = Direction.UP

    def move_up(self):
        if (self.direction != Direction.DOWN):
            self.direction = Direction.UP

    def move_down(self):
        if (self.direction != Direction.UP):
            self.direction = Direction.DOWN

    def move_left(self):
        if (self.direction != Direction.RIGHT):
            self.direction = Direction.LEFT

    def move_right(self):
        if (self.direction != Direction.LEFT):
            self.direction = Direction.RIGHT

    def move(self, action):
        if action == Direction.UP:
            self.move_up()
        elif action == Direction.DOWN:
            self.move_down()
        elif action == Direction.LEFT:
            self.move_left()
        elif action == Direction.RIGHT:
            self.move_right()

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

    def collision(self, enemy_x, enemy_y):
        (head_x, head_y) = self.head()

        crashing_in_enemy = False
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
