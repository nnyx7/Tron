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
    HIT = [0, 0, 1]
    EMPTY = [1, 0, 0]
    PLAYER_HEAD = [0, 1, 0]
    ENEMY_HEAD = PLAYER_HEAD
