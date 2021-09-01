import tensorflow as tf

from enemy import Enemy, SmarterEnemy
from model_wrapper import ModelWrapper
from structs import Result, Encodings3, Encodings4, Encodings5, Encodings
from game import Game, BLOCK_SIZE


def evaluate(agent, grid_size, board_size, encodings, rotated, num_games, enemy_constructor=None, ui=False, interval=0.1):
    game = Game(encodings, update_interval=interval,
                board_size=board_size, ui=ui, with_enemy=True)
    if enemy_constructor:
        enemy = enemy_constructor(game.enemy, encodings)
    else:
        enemy = agent

    results = {Result.WIN: 0, Result.DRAW: 0, Result.LOSE: 0}

    for i in range(num_games):
        game.reset()
        if (i % (num_games // 100) == 0):
            print(f'games played: {i}')
        while not game.has_ended():
            state = game.state

            grid_state = game.grid(grid_size)
            agent_action = agent(grid_state, game.player.direction, rotated)

            if enemy_constructor:
                enemy_action = enemy(state)
            else:
                grid_state = game.grid(grid_size, center='enemy')
                enemy_action = agent(grid_state, game.enemy.direction, rotated)

            _, has_ended, result = game.step(
                agent_action, enemy_action, wait=ui)

            if has_ended:
                if result == Result.WIN.value:
                    results[Result.WIN] += 1
                elif result == Result.DRAW.value:
                    results[Result.DRAW] += 1
                elif result == Result.LOSE.value:
                    results[Result.LOSE] += 1

    return results


def evaluate_without_enemy(agent, grid_size, board_size, encodings, rotated, ui=False, interval=0.1):
    game = Game(encodings, update_interval=interval,
                board_size=board_size, ui=ui)

    total_reward = 0

    for j in range(board_size[1]):
        for i in range(board_size[0]):
            game.reset(player_init_pos=(i * BLOCK_SIZE, j * BLOCK_SIZE))
            reward = 0
            while not game.has_ended():
                grid_state = game.grid(grid_size)
                agent_action = agent(
                    grid_state, game.player.direction, rotated)

                _, has_ended, _ = game.step(agent_action, None, wait=ui)

                if has_ended:
                    total_reward += reward
                else:
                    reward += 1

    return total_reward / (board_size[0] * board_size[1])


if __name__ == "__main__":
    game = Game(Encodings3, with_enemy=True)

    enemy = SmarterEnemy(game.enemy, Encodings3)
    model = tf.keras.models.load_model('model.h5', compile=False)
    agent = ModelWrapper(model)

    game.run_agent_vs_enemy(agent, enemy, False, grid_size=5)
