import numpy as np
import tensorflow as tf
import random

from helpers import best_possible_action


class Agent:
    __clockwise = {0: 0, 1: 2, 2: 3, 3: 1}
    __rev_clockwise = {0: 0, 1: 3, 2: 1, 3: 2}

    def __init__(self, model, num_actions, min_epsilon, max_epsilon, epsilon_decay_rate):
        self.model = model()
        self.target_model = model()
        self.update_target_model()

        self.num_actions = num_actions

        self.min_epsilon = min_epsilon
        self.max_epsilon = max_epsilon
        self.epsilon_decay_rate = epsilon_decay_rate
        self.epsilon = max_epsilon

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def __explore(self):
        return random.randrange(self.num_actions)

    def __exploit(self, state, direction):
        state_tensor = tf.convert_to_tensor(state)
        state_tensor = tf.expand_dims(state_tensor, 0)
        actions = self.model(state_tensor, training=False)

        action = tf.argmax(actions[0]).numpy()

        if direction and direction != 'up':

            if direction == 'right':
                shift = 1
            elif direction == 'down':
                shift = 2
            elif direction == 'left':
                shift = 3

            action = Agent.__rev_clockwise[(
                Agent.__clockwise[action] + shift) % self.num_actions]

        return action

    def action(self, state, direction=None):
        if random.random() > self.epsilon:
            return self.__exploit(state, direction)
        else:
            return self.__explore()

    def decay_epsilon(self, episode):
        self.epsilon = self.min_epsilon + \
            (self.max_epsilon - self.min_epsilon) * \
            np.exp(-episode * self.epsilon_decay_rate)
