import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import os
from src.constants import *


# ── direction tuple → which of the 4 direction channels to set ──
_DIR_CHANNEL = {
    (1,  0): 4,   # right
    (-1, 0): 5,   # left
    (0, -1): 6,   # up
    (0,  1): 7,   # down
}

def grid_to_state(grid, direction):
    """
    Convert a 2D grid + direction into an 8-channel tensor.

    grid      : (H, W) int32 array  — 0 empty / 1 body / 2 food / 3 head
    direction : (dx, dy) tuple      — e.g. (1,0) for right

    Returns   : (8, H, W) float32 array
        ch 0-3  →  one-hot cell types
        ch 4-7  →  one-hot direction, broadcast across all cells
    """
    grid = np.array(grid, dtype=np.int32)
    H, W = grid.shape
    state = np.zeros((8, H, W), dtype=np.float32)

    # Cell type channels
    for c in range(4):
        state[c] = (grid == c).astype(np.float32)

    # Direction channel (entire plane set to 1.0 for the active direction)
    if direction in _DIR_CHANNEL:
        state[_DIR_CHANNEL[direction]] = 1.0

    return state  # (8, H, W)



# ─────────────────────────────────────────────
#  CNN Q-Network
# ─────────────────────────────────────────────
class DQN(nn.Module):
    def __init__(self, grid_h, grid_w, action_dim, n_channels=8):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(n_channels, 32, kernel_size=3, padding=1),  
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
        )

        conv_out = 64 * grid_h * grid_w

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(conv_out, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, action_dim),
        )

    def forward(self, x):
        return self.fc(self.conv(x))


# ─────────────────────────────────────────────
#  Trainer
# ─────────────────────────────────────────────
class DQNTrainer:
    """
    Policy net + target net + optimizer + training logic.

    Key improvements vs the old MLP version:
        • CNN input  – spatial structure preserved
        • Double DQN – separates action selection from evaluation (less overestimation)
        • Huber loss – stable against Q-value outliers
        • Grad clipping – prevents exploding gradients
    """

    def __init__(self, lr, grid_h=CELL_NUMBER, grid_w=CELL_NUMBER, action_dim=3, gamma=0.99):
        self.grid_h = grid_h
        self.grid_w = grid_w
        self.action_dim = action_dim
        self.gamma = gamma
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"using: {self.device}")

        self.policy_net = DQN(grid_h, grid_w, action_dim).to(self.device)
        self.target_net = DQN(grid_h, grid_w, action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()   # target net is never trained directly

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.criterion = nn.SmoothL1Loss()  # Huber loss

    # ── Action selection ──────────────────────
    def select_action(self, state, epsilon):
        """
        state: numpy array (4, H, W)  ←  output of grid_to_state()
        """
        if random.random() < epsilon:
            return random.randrange(self.action_dim)
        with torch.no_grad():
            t = torch.FloatTensor(state).unsqueeze(0).to(self.device)  # (1, 4, H, W)
            return self.policy_net(t).argmax().item()

    # ── Training step ─────────────────────────
    def train_step(self, batch):
        """
        batch: list of (state, next_state, action, reward, done)
               where state / next_state are (4, H, W) numpy arrays
        """
        states, next_states, actions, rewards, dones = zip(*batch)

        states      = torch.FloatTensor(np.array(states)).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        actions     = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards     = torch.FloatTensor(rewards).to(self.device)
        dones       = torch.FloatTensor(dones).to(self.device)

        q_values = self.policy_net(states).gather(1, actions).squeeze(1)

        with torch.no_grad():
            next_actions = self.policy_net(next_states).argmax(1, keepdim=True)
            max_next_q   = self.target_net(next_states).gather(1, next_actions).squeeze(1)
            target_q     = rewards + self.gamma * max_next_q * (1 - dones)

        self.loss = self.criterion(q_values, target_q)
        self.optimizer.zero_grad()
        self.loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=10)
        self.optimizer.step()

        # return self.loss.item()
        return self.loss

    # ── Target network sync ───────────────────
    def update_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())

    # ── Persistence ───────────────────────────
    def save(self, file_name='model.pth'):
        os.makedirs('./model', exist_ok=True)
        path = os.path.join('./model', file_name)
        torch.save(self.policy_net.state_dict(), path)
        print(f"Model saved to {path}")

    def load(self, file_name='model.pth'):
        path = os.path.join('./model', file_name)
        if os.path.exists(path):
            weights = torch.load(path, weights_only=True)
            self.policy_net.load_state_dict(weights)
            self.target_net.load_state_dict(weights)
            self.policy_net.train()   # ready to keep training
            self.target_net.eval()
            print(f"Model loaded from {path}")
        else:
            print(f"No saved model found at {path}, starting fresh.")