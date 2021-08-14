from enum import Enum


class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


class Result(Enum):
    WIN = 'win'
    LOSE = 'lose'
    DRAW = 'draw'
    UNKNOWN = 'unknown'


class Encodings(Enum):
    WALL_HIT = [-1, -1, -1, 1]
    PLAYER_HEAD = [-1, 1, -1, -1]
    PLAYER_BODY = [-1, -1, 1, -1]
    # ENEMY_HEAD = 20
    # ENEMY_BODY = 2
    EMPTY = [1, -1, -1, -1]
