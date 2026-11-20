import random
import numpy as np
from src.game import AI
from src.model import DQNTrainer
from collections import deque
from src.constants import *

class Agent():
    def __init__(self, lr):
        self.memory = deque(maxlen=MAX_MEMORY)
        self.trainer = DQNTrainer(lr=lr, action_dim=3)
        self.trainer.load()
        self.n_games = 0
    
    def get_state(self, game:AI):
        state_arr = game.get_state()
        state = np.array(state_arr)
        return state

    def get_action(self, state):
        # epsilon = 0.01
        epsilon = max(0.01, 0.995 ** self.n_games)
        action = self.trainer.select_action(state, epsilon)
        return action
    
    def train_long_memory(self):
        batch = random.sample(self.memory, 256) if len(self.memory) > 256 else self.memory
        return self.trainer.train_step(batch)
    
    def train_short_memory(self, old_state, new_state, action, reward, gameover):
        batch = [(old_state, new_state, action, reward, gameover)]
        self.trainer.train_step(batch)
    
    def remember(self, old_state, new_state, action, reward, gameover):
        self.memory.append((old_state, new_state, action, reward, gameover))
    
    def get_loss(self):
        return self.trainer.loss
    
