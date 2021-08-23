import numpy as np
from helpers import best_possible_action


class ModelWrapper:
    def __init__(self, model):
        self.model = model

    def __call__(self, state, direction):
        actions = self.model(np.array([state]))
        best_action = best_possible_action(actions, direction)
        return best_action
