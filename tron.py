import pygame
from pygame.locals import *
import time
import numpy as np
import tensorflow as tf

from constants import *
from enemy import Enemy
from helpers import best_possible_action, flatten_grid
from player import Player
from structs import Direction, Encodings, Result


PLAYER_KEYS = {K_UP: Direction.UP, K_DOWN: Direction.DOWN,
               K_LEFT: Direction.LEFT, K_RIGHT: Direction.RIGHT}

ENEMY_KEYS = {K_w: Direction.UP, K_s: Direction.DOWN,
              K_a: Direction.LEFT, K_d: Direction.RIGHT}


class Game:
    actions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

    def __init__(self, update_interval=INTERVAL, board_size=BOARD_SIZE, player_keys=PLAYER_KEYS, enemy_keys=ENEMY_KEYS,  ui=True, with_enemy=False):
        self.update_interval = update_interval
        self.player_keys = player_keys
        self.enemy_keys = enemy_keys
        self.ui = ui
        self.with_enemy = with_enemy

        (max_x_index, max_y_index) = board_size

        self.screen_size = (max_x_index * BLOCK_SIZE, max_y_index * BLOCK_SIZE)

        self.state = []
        for i in range(max_x_index):
            self.state.append([])
            for j in range(max_y_index):
                self.state[i].append(Encodings.EMPTY.value)

        if self.with_enemy:
            # Random on the upper half of the board
            self.player = Player(
                (0, max_x_index), (0, max_y_index // 2), self.screen_size)
            # Random pn the lower half of the board
            self.enemy = Player(
                (0, max_x_index), (max_y_index // 2, max_y_index), self.screen_size)

        else:
            self.player = Player(
                (0, max_x_index), (0, max_y_index), self.screen_size)
            self.enemy = None

        if (self.ui):
            self.enable_ui()

        self.result = Result.UNKNOWN
        self.steps_counter = 0
        self.reset()

    def enable_ui(self):
        self.ui = True
        pygame.init()
        self.surface = pygame.display.set_mode(self.screen_size)
        self.player_block = pygame.image.load("assets/blue.png").convert()
        self.enemy_block = pygame.image.load("assets/yellow.png").convert()

    def reset(self):
        self.result = Result.UNKNOWN
        self.steps_counter = 0

        (size_x, size_y) = self.screen_size
        for i in range(size_x // BLOCK_SIZE):
            for j in range(size_y // BLOCK_SIZE):
                self.state[i][j] = Encodings.EMPTY.value

        self.player.reset()
        (player_x, player_y) = self.player.head_indexes()
        self.state[player_x][player_y] = Encodings.PLAYER_HEAD.value

        if self.with_enemy:
            self.enemy.reset()
            (enemy_x, enemy_y) = self.enemy.head_indexes()
            self.state[enemy_x][enemy_y] = Encodings.ENEMY_HEAD.value

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

    def __update_state(self):
        # Player
        (prev_x, prev_y) = self.player.prev_head_indexes()
        self.state[prev_x][prev_y] = Encodings.HIT.value

        if not self.player.collision_with_wall():
            (x, y) = self.player.head_indexes()
            self.state[x][y] = Encodings.PLAYER_HEAD.value

        if self.with_enemy:
            # Enemy
            (prev_x, prev_y) = self.enemy.prev_head_indexes()
            self.state[prev_x][prev_y] = Encodings.HIT.value

            if not self.enemy.collision_with_wall():
                (x, y) = self.enemy.head_indexes()
                self.state[x][y] = Encodings.ENEMY_HEAD.value

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

    def print_state(self):
        state_string = ""
        for j in range(len(self.state[0])):
            for i in range(len(self.state)):
                state_string += f'{self.state[i][j]} '
            state_string += '\n'

        print(state_string)

    def __try_as_index(action):
        try:
            return Game.actions[int(action)]
        except:
            return action

    def step(self, action, enemy_action, wait=False):
        if self.result == Result.UNKNOWN:
            action = Game.__try_as_index(action)
            self.player.move(action, self.steps_counter == 0)
            self.player.progress()

            if self.with_enemy:
                enemy_action = Game.__try_as_index(enemy_action)
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

    def has_ended(self):
        return self.result != Result.UNKNOWN

    def run(self):
        running = True
        time.sleep(self.update_interval)

        while running:
            player_action = None
            enemy_action = None

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key in self.player_keys:
                        player_action = self.player_keys[event.key]
                    elif event.key in self.enemy_keys:
                        enemy_action = self.enemy_keys[event.key]
                    elif event.key == K_r:
                        self.reset()
                        time.sleep(self.update_interval)
                elif event.type == QUIT:
                    running = False

            self.step(player_action, enemy_action, wait=True)

    def run_against_enemy(self, enemy):
        if not self.with_enemy:
            raise("Enemy presence is not enabled")

        running = True
        time.sleep(self.update_interval)

        while running:
            player_action = None

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key in self.player_keys:
                        player_action = self.player_keys[event.key]
                    elif event.key == K_r:
                        self.reset()
                        time.sleep(self.update_interval)

                elif event.type == QUIT:
                    running = False

            if self.result == Result.UNKNOWN:
                self.step(player_action, enemy.action(self.state), wait=True)

    def run_agent_vs_enemy(self, agent, enemy):
        if not self.with_enemy:
            raise("Enemy presence is not enabled")

        running = True
        time.sleep(self.update_interval)

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_r:
                        self.reset()
                        time.sleep(self.update_interval)
                elif event.type == QUIT:
                    running = False

            if self.result == Result.UNKNOWN:
                grid_state = flatten_grid(
                    self.state, game.player.head_indexes(), 3)
                agent_actions = agent(np.array([grid_state]))
                agent_action = best_possible_action(
                    agent_actions, self.player.direction)

                enemy_action = enemy.action(self.state)
                self.step(agent_action, enemy_action, wait=True)


if __name__ == "__main__":
    game = Game()

    enemy = Enemy(game.enemy)
    model = tf.keras.models.load_model('model.h5', compile=False)

    game.run_agent_vs_enemy(model, enemy)
