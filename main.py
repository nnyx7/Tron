from enum import Enum
import pygame
from pygame.locals import *
import time

BOARD_SIZE = (660, 450)
BLOCK_SIZE = 30
INTERVAL = 0.07
BACKGROUND_COLOR = (44, 41, 87)


class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


PLAYER_KEYS = {Direction.UP.value: K_UP, Direction.DOWN.value: K_DOWN,
               Direction.LEFT.value: K_LEFT, Direction.RIGHT.value: K_RIGHT}

ENEMY_KEYS = {Direction.UP.value: K_w, Direction.DOWN.value: K_s,
              Direction.LEFT.value: K_a, Direction.RIGHT.value: K_d}


class GAME_RESULT(Enum):
    WIN = 'win'
    LOSE = 'lose'
    DRAW = 'draw'
    UNKNOWN = 'unknown'


class ENCODINGS(Enum):
    WALL_HIT = 3
    PLAYER_HEAD = 10
    PLAYER_BODY = 1
    ENEMY_HEAD = 20
    ENEMY_BODY = 2


def pos_to_indexes(position):
    return (int(position[0] // BLOCK_SIZE), int(position[1] // BLOCK_SIZE))


class Player:
    def __init__(self, init_coordinates, board_size, keys):
        self.length = 1
        self.x = [init_coordinates[0]]
        self.y = [init_coordinates[1]]
        self.board_size = board_size
        self.keys = keys
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

    def move_on_key(self, key):
        if key == self.keys[Direction.UP.value]:
            self.move_up()
        elif key == self.keys[Direction.DOWN.value]:
            self.move_down()
        elif key == self.keys[Direction.LEFT.value]:
            self.move_left()
        elif key == self.keys[Direction.RIGHT.value]:
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

    def prev_head(self):
        prev_index = self.length - 2
        return (self.x[prev_index], self.y[prev_index])

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


class Game:
    def __init__(self, enemy_logic, update_interval=INTERVAL, board_size=BOARD_SIZE, player_keys=PLAYER_KEYS, enemy_keys=ENEMY_KEYS,  ui=True):
        self.update_interval = update_interval
        self.board_size = board_size
        self.enemy_logic = enemy_logic
        self.player_keys = player_keys
        self.enemy_keys = enemy_keys
        self.ui = ui

        if (self.ui):
            pygame.init()
            self.surface = pygame.display.set_mode(board_size)
            self.player_block = pygame.image.load("assets/blue.png").convert()
            self.enemy_block = pygame.image.load("assets/yellow.png").convert()

        self.reset()

    def reset(self):
        self.status = GAME_RESULT.UNKNOWN

        self.state = []
        (size_x, size_y) = self.board_size
        for i in range(size_x // BLOCK_SIZE):
            self.state.append([])
            for j in range(size_y // BLOCK_SIZE):
                self.state[i].append(0)

        # Initializing the player
        player_pos = (size_x / 4, size_y - BLOCK_SIZE)
        self.player = Player(player_pos, self.board_size, self.player_keys)
        # Initializing the enemy
        enemy_pos = (size_x / 4 * 3, size_y - BLOCK_SIZE)
        self.enemy = Player(enemy_pos, self.board_size, self.enemy_keys)

        (player_x, player_y) = pos_to_indexes(self.player.head())
        self.state[player_x][player_y] = ENCODINGS.PLAYER_HEAD.value

        (enemy_x, enemy_y) = pos_to_indexes(self.enemy.head())
        self.state[enemy_x][enemy_y] = ENCODINGS.ENEMY_HEAD.value

        if (self.ui):
            self.surface.fill(BACKGROUND_COLOR)
            self.update_ui()

    def update_state(self):
        # Player
        (prev_x, prev_y) = pos_to_indexes(self.player.prev_head())
        (x, y) = pos_to_indexes(self.player.head())

        if self.player.collision_with_wall():
            self.state[prev_x][prev_y] += ENCODINGS.WALL_HIT.value
        else:
            self.state[prev_x][prev_y] += (ENCODINGS.PLAYER_BODY.value -
                                           ENCODINGS.PLAYER_HEAD.value)
            self.state[x][y] += ENCODINGS.PLAYER_HEAD.value

        # Enemy
        (prev_x, prev_y) = pos_to_indexes(self.enemy.prev_head())
        (x, y) = pos_to_indexes(self.enemy.head())

        if self.enemy.collision_with_wall():
            self.state[prev_x][prev_y] += ENCODINGS.WALL_HIT.value
        else:
            self.state[prev_x][prev_y] += (ENCODINGS.ENEMY_BODY.value -
                                           ENCODINGS.ENEMY_HEAD.value)
            self.state[x][y] += ENCODINGS.ENEMY_HEAD.value

    def __print_state(self):
        state_string = ""
        for j in range(len(self.state[0])):
            for i in range(len(self.state)):
                state_string += f'{self.state[i][j]} '
            state_string += '\n'

        print(state_string)

    def update_result(self):
        has_player_lost = self.player.collision(self.enemy.x, self.enemy.y)
        has_enemy_lost = self.enemy.collision(self.player.x, self.player.y)

        if has_player_lost and has_enemy_lost:
            self.status = GAME_RESULT.DRAW
        elif has_player_lost:
            self.status = GAME_RESULT.LOSE
        elif has_enemy_lost:
            self.status = GAME_RESULT.WIN

    def display_result(self):
        font = pygame.font.SysFont('arial', 30)
        result = font.render(self.status.value, True, (255, 255, 255))

        x = (self.surface.get_width() - result.get_width()) // 2
        y = (self.surface.get_height() - result.get_height()) // 2

        self.surface.blit(result, (x, y))
        pygame.display.flip()

    def update_ui(self):
        # Draw player
        for i in range(self.player.length):
            self.surface.blit(self.player_block,
                              (self.player.x[i], self.player.y[i]))
        # Draw enemy
        for i in range(self.enemy.length):
            self.surface.blit(self.enemy_block,
                              (self.enemy.x[i], self.enemy.y[i]))
        pygame.display.flip()

    def run(self):
        running = True

        while running:
            last_player_key = None
            last_enemy_key = None

            if (self.ui):
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            running = False
                        elif event.key in self.player_keys.values():
                            last_player_key = event.key
                        elif event.key in self.enemy_keys.values():
                            last_enemy_key = event.key
                        elif event.key == K_r:
                            self.reset()

                    elif event.type == QUIT:
                        running = False

            self.player.move_on_key(last_player_key)
            self.enemy.move_on_key(last_enemy_key)

            if self.status == GAME_RESULT.UNKNOWN:
                self.player.progress()
                self.enemy.progress()
                self.update_state()
                self.update_result()

                if (self.ui):
                    self.update_ui()
                    if self.status != GAME_RESULT.UNKNOWN:
                        self.display_result()

                time.sleep(self.update_interval)


if __name__ == "__main__":
    game = Game(None)
    game.run()
