import random


class ReplayMemory:
    def __init__(self, capacity):
        self.memory = []
        self.__capacity = capacity
        self.__add_index = 0

    def add(self, experience):
        if not(len(self.memory) == self.__capacity):
            self.memory.append(experience)
        else:
            self.memory[self.__add_index] = experience
            self.__add_index = (self.__add_index + 1) % self.__capacity

    def sample(self, batch_size):
        return random.choices(self.memory, k=batch_size)

    def can_provide_batch(self, batch_size):
        return len(self.memory) >= batch_size
        # return True
