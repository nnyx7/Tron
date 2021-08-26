from structs import Direction
import numpy as np
import tensorflow as tf
import random


class Agent:
    __mapping = {Direction.UP: [0, 1, 2, 3], Direction.LEFT: [3, 2, 0, 1],
                 Direction.DOWN: [1, 0, 3, 2], Direction.RIGHT: [2, 3, 1, 0]}

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
            action = (action, Agent.__mapping[direction][action])
        return action

    def __exploit(self, state, direction):
        state_tensor = tf.convert_to_tensor(state)
        state_tensor = tf.expand_dims(state_tensor, 0)
        actions = self.model(state_tensor, training=False)

        if direction:
            actions = tf.argsort(actions[0].numpy())
            if direction != Direction.UP:
                actions = [(action.numpy(), Agent.__mapping[direction][action])
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
