from helpers import ROTATING_ACTIONS
from structs import Direction
import numpy as np
import tensorflow as tf
import random


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

    def __explore(self, direction):
        action = random.randrange(self.num_actions)
        if direction:
            action = (action, ROTATING_ACTIONS[direction][action])
        return action

    def __exploit(self, state, direction):
        state = np.expand_dims(state, axis=0)
        actions = self.model(state, training=False)

        if direction:
            actions = tf.argsort(actions[0].numpy())
            if direction != Direction.UP:
                actions = [(action.numpy(), ROTATING_ACTIONS[direction][action])
                           for action in actions]
                action = actions[self.num_actions - 1]
            else:
                action = (actions[self.num_actions - 1],
                          actions[self.num_actions - 1])
        else:
            action = tf.argmax(actions[0]).numpy()

        return action

    def action(self, state, direction=None):
        if random.random() > self.epsilon:
            return self.__exploit(state, direction)
        else:
            return self.__explore(direction)

    def decay_epsilon(self, episode):
        self.epsilon = self.min_epsilon + \
            (self.max_epsilon - self.min_epsilon) * \
            np.exp(-episode * self.epsilon_decay_rate)
