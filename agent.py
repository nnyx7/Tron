import numpy as np
import tensorflow as tf
import random

from helpers import best_possible_action


class Agent:
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
        action = best_possible_action(actions, direction)
        return action

    def action(self, state, direction):
        if random.random() > self.epsilon:
            return self.__exploit(state, direction)
        else:
            return self.__explore()

    def decay_epsilon(self, episode):
        self.epsilon = self.min_epsilon + \
            (self.max_epsilon - self.min_epsilon) * \
            np.exp(-episode * self.epsilon_decay_rate)
