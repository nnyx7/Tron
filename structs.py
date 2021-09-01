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


class Encodings3(Enum):
    HIT = [0, 0, 1]
    EMPTY = [1, 0, 0]
    PLAYER_HEAD = [0, 1, 0]
    PLAYER_BODY = HIT
    ENEMY_HEAD = PLAYER_HEAD
    ENEMY_BODY = HIT


class Encodings4(Enum):
    HIT = [0, 0, 0, 1]
    EMPTY = [1, 0, 0, 0]
    PLAYER_HEAD = [0, 1, 0, 0]
    PLAYER_BODY = HIT
    ENEMY_HEAD = PLAYER_HEAD
    ENEMY_BODY = [0, 0, 1, 0]
