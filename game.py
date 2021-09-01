import pygame
from pygame.locals import *
import time
import numpy as np

from player import Player
from structs import Direction, Result

BOARD_SIZE = (6, 6)
BLOCK_SIZE = 30
INTERVAL = 0.07
BACKGROUND_COLOR = (44, 41, 87)

ACTIONS = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

PLAYER_KEYS = {K_UP: Direction.UP, K_DOWN: Direction.DOWN,
               K_LEFT: Direction.LEFT, K_RIGHT: Direction.RIGHT}

ENEMY_KEYS = {K_w: Direction.UP, K_s: Direction.DOWN,
              K_a: Direction.LEFT, K_d: Direction.RIGHT}


class Game:
    actions = ACTIONS

    def __init__(self, encodings, update_interval=INTERVAL, board_size=BOARD_SIZE,
                 player_keys=PLAYER_KEYS, enemy_keys=ENEMY_KEYS,  ui=True, with_enemy=False):

        self.encodings = encodings
        self.update_interval = update_interval
        self.board_size = board_size
        self.player_keys = player_keys
        self.enemy_keys = enemy_keys
        self.ui = ui
        self.with_enemy = with_enemy

        (max_x_index, max_y_index) = self.board_size

        self.screen_size = (max_x_index * BLOCK_SIZE, max_y_index * BLOCK_SIZE)

        self.state = []
        for i in range(max_x_index):
            self.state.append([])
            for j in range(max_y_index):
                self.state[i].append(self.encodings.EMPTY.value)

        if self.with_enemy:
            # Random on the upper half of the board
            self.player = Player(
                (0, max_x_index), (0, max_y_index), self.screen_size, self.actions, BLOCK_SIZE)
            # Random pn the lower half of the board
            self.enemy = Player(
                (0, max_x_index), (0, max_y_index), self.screen_size, self.actions, BLOCK_SIZE)

        else:
            self.player = Player(
                (0, max_x_index), (0, max_y_index), self.screen_size, self.actions, BLOCK_SIZE)
            self.enemy = None

        if (self.ui):
            self.__enable_ui()

        self.result = Result.UNKNOWN
        self.steps_counter = 0
        self.reset()

    def reset(self, player_init_pos=None, enemy_init_pos=None):
        self.result = Result.UNKNOWN
        self.steps_counter = 0

        (size_x, size_y) = self.screen_size
        for i in range(size_x // BLOCK_SIZE):
            for j in range(size_y // BLOCK_SIZE):
                self.state[i][j] = self.encodings.EMPTY.value

        self.player.reset(init_pos=player_init_pos)
        (player_x, player_y) = self.player.head_indexes()
        self.state[player_x][player_y] = self.encodings.PLAYER_HEAD.value

        if self.with_enemy:
            self.enemy.reset(init_pos=enemy_init_pos)
            while (self.enemy.x == self.player.x and self.enemy.y == self.player.y):
                self.enemy.reset()
            (enemy_x, enemy_y) = self.enemy.head_indexes()
            self.state[enemy_x][enemy_y] = self.encodings.ENEMY_HEAD.value

        if (self.ui):
            self.surface.fill(BACKGROUND_COLOR)
            # Vertical lines
            for i in range(int(self.screen_size[0] // BLOCK_SIZE)):
                pygame.draw.line(self.surface, (150, 150, 150), (i *
                                 BLOCK_SIZE, 0), (i * BLOCK_SIZE, self.screen_size[1]))
            # Horizontal lines
            for i in range(int(self.screen_size[1] // BLOCK_SIZE)):
                pygame.draw.line(self.surface, (150, 150, 150), (0, i *
                                 BLOCK_SIZE), (self.screen_size[0], i * BLOCK_SIZE))

            self.__update_ui()

    def step(self, action, enemy_action, wait=False):
        def try_as_index(action):
            try:
                return Game.actions[int(action)]
            except:
                return action

        if self.result == Result.UNKNOWN:
            action = try_as_index(action)
            self.player.move(action, self.steps_counter == 0)
            self.player.progress()

            if self.with_enemy:
                enemy_action = try_as_index(enemy_action)
                self.enemy.move(enemy_action, self.steps_counter == 0)
                self.enemy.progress()

            self.__update_state()
            self.__update_result()

            self.steps_counter += 1

            if (self.ui):
                self.__update_ui()
                if self.result != Result.UNKNOWN:
                    self.__display_result()
        if wait:
            time.sleep(self.update_interval)

        return (self.state, self.result != Result.UNKNOWN, self.result.value)

    def __grid(self, side_size, center='player'):
        grid_state = []
        for i in range(side_size):
            grid_state.append([])
            for j in range(side_size):
                grid_state[i].append(self.encodings.EMPTY.value)

        (board_x, board_y) = self.board_size
        offset = int(-(side_size - 1) // 2)

        if center == 'player':
            (x, y) = self.player.head_indexes()
        elif center == 'enemy':
            (x, y) = self.enemy.head_indexes()
        else:
            (x, y) = center

        offset_x = offset
        for i in range(side_size):
            actual_x = x + offset_x

            offset_y = offset
            for j in range(side_size):
                actual_y = y + offset_y
                if (actual_x < 0 or actual_x >= board_x or actual_y < 0 or actual_y >= board_y):
                    grid_state[i][j] = self.encodings.HIT.value
                else:
                    grid_state[i][j] = self.state[actual_x][actual_y]
                offset_y += 1
            offset_x += 1

        return grid_state

    def grid(self, side_size, center='player'):
        return np.array(self.__grid(side_size, center)).flatten()

    def rotated_grid(self, side_size, center='player'):
        grid_state = self.__grid(side_size, center)

        if center == 'player':
            direction = self.player.direction
        elif center == 'enemy':
            direction = self.enemy.direction

        if direction == Direction.LEFT:
            grid_state = np.rot90(grid_state, k=1)
        elif direction == Direction.RIGHT:
            grid_state = np.rot90(grid_state, k=-1)
        elif direction == Direction.DOWN:
            grid_state = np.rot90(grid_state, k=2)

        return np.array(grid_state).flatten()

    def has_ended(self):
        return self.result != Result.UNKNOWN

    def run(self):
        running = True
        time.sleep(self.update_interval)

        while running:
            player_action = None
            enemy_action = None

            for event in pygame.event.get():
                running = self.__resolve_game_controls(event, running)
                if event.type == KEYDOWN:
                    if event.key in self.player_keys:
                        player_action = self.player_keys[event.key]
                    elif event.key in self.enemy_keys:
                        enemy_action = self.enemy_keys[event.key]

            self.step(player_action, enemy_action, wait=True)

    def run_against_enemy(self, enemy):
        if not self.with_enemy:
            raise("Enemy presence is not enabled")

        running = True
        time.sleep(self.update_interval)

        while running:
            player_action = None

            for event in pygame.event.get():
                running = self.__resolve_game_controls(event, running)
                if event.type == KEYDOWN and event.key in self.player_keys:
                    player_action = self.player_keys[event.key]

            if self.result == Result.UNKNOWN:
                self.step(player_action, enemy(self.state), wait=True)

    def run_agent(self, agent, rotated, grid_size=3):
        running = True
        time.sleep(self.update_interval)

        while running:
            for event in pygame.event.get():
                running = self.__resolve_game_controls(event, running)

            if self.result == Result.UNKNOWN:
                grid_state = self.grid(grid_size)
                agent_action = agent(
                    grid_state, self.player.direction, rotated)
                self.step(agent_action, None, wait=True)

    def run_agent_vs_enemy(self, agent, enemy, rotated, grid_size=3):
        if not self.with_enemy:
            raise("Enemy presence is not enabled")

        running = True
        time.sleep(self.update_interval)

        while running:
            for event in pygame.event.get():
                running = self.__resolve_game_controls(event, running)

            if self.result == Result.UNKNOWN:
                grid_state = self.grid(grid_size)
                agent_action = agent(
                    grid_state, self.player.direction, rotated)

                enemy_action = enemy(self.state)
                self.step(agent_action, enemy_action, wait=True)

    def print_state(self):
        state_string = ""
        for j in range(len(self.state[0])):
            for i in range(len(self.state)):
                state_string += f'{self.state[i][j]} '
            state_string += '\n'

        print(state_string)

    def __resolve_game_controls(self, event, running):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_r:
                self.reset()
                time.sleep(self.update_interval)
        elif event.type == QUIT:
            running = False

        return running

    def __enable_ui(self):
        self.ui = True
        pygame.init()
        self.surface = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption('Tron')
        self.player_block = pygame.image.load("assets/blue.png").convert()
        self.enemy_block = pygame.image.load("assets/yellow.png").convert()

    def __update_state(self):
        # Player
        (prev_x, prev_y) = self.player.prev_head_indexes()

        if self.player.collision_with_wall():
            self.state[prev_x][prev_y] = self.encodings.HIT.value
        else:
            self.state[prev_x][prev_y] = self.encodings.PLAYER_BODY.value
            (x, y) = self.player.head_indexes()
            self.state[x][y] = self.encodings.PLAYER_HEAD.value

        if self.with_enemy:
            # Enemy
            (prev_x, prev_y) = self.enemy.prev_head_indexes()
            if self.enemy.collision_with_wall():
                self.state[prev_x][prev_y] = self.encodings.HIT.value
            else:
                self.state[prev_x][prev_y] = self.encodings.ENEMY_BODY.value
                (x, y) = self.enemy.head_indexes()
                self.state[x][y] = self.encodings.ENEMY_HEAD.value

    def __update_result(self):
        if self.with_enemy:
            has_player_lost = self.player.collision(
                (self.enemy.x, self.enemy.y))
            has_enemy_lost = self.enemy.collision(
                (self.player.x, self.player.y))

            if has_player_lost and has_enemy_lost:
                self.result = Result.DRAW
            elif has_player_lost:
                self.result = Result.LOSE
            elif has_enemy_lost:
                self.result = Result.WIN
        else:
            if self.player.collision(enemy_positions=None):
                self.result = Result.LOSE

    def __display_result(self):
        font = pygame.font.SysFont('arial', 30)
        result = font.render(self.result.value, True, (255, 255, 255))

        x = (self.surface.get_width() - result.get_width()) // 2
        y = (self.surface.get_height() - result.get_height()) // 2

        self.surface.blit(result, (x, y))
        pygame.display.flip()

    def __update_ui(self):
        # Draw player
        for i in range(self.player.length):
            self.surface.blit(self.player_block,
                              (self.player.x[i], self.player.y[i]))
        if self.with_enemy:
            # Draw enemy
            for i in range(self.enemy.length):
                self.surface.blit(self.enemy_block,
                                  (self.enemy.x[i], self.enemy.y[i]))

        pygame.display.flip()
