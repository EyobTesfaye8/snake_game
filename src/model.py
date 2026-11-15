import torch
import torch.nn as nn
import torch.optim as optim
import random
import os

class DQN(nn.Module):
    """The Neural Network architecture."""
    def __init__(self, state_dim, action_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_dim, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 256)
        self.fc3 = nn.Linear(256, action_dim)  # Output layer: one Q-value per action

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)


class DQNTrainer:
    """Encapsulates the policy network, target network, optimizer, and training logic."""
    def __init__(self, lr, state_dim=11, action_dim=3, gamma=0.99):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        
        # Initialize networks
        self.policy_net = DQN(state_dim, action_dim)
        self.target_net = DQN(state_dim, action_dim)
        self.target_net.load_state_dict(self.policy_net.state_dict()) # Copy weights for stability
        
        # Training tools
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

    def select_action(self, state, epsilon):
        """Chooses an action using an epsilon-greedy strategy."""
        if random.random() < epsilon:
            return random.randrange(self.action_dim)  # Explore: random action
        else:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                q_values = self.policy_net(state_tensor)
                return q_values.argmax().item()  # Exploit: best predicted action

    def train_step(self, batch):
        """Performs a single gradient descent step on a batch of experiences."""
        # Unpack batch elements
        # old_state, new_state, action, reward, gameover
        states, next_states, actions, rewards, dones = zip(*batch)
        
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions).unsqueeze(1)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # 1. Predict Q-values for current states
        q_values = self.policy_net(states).gather(1, actions).squeeze(1)

        # 2. Compute target Q-values using the Bellman Equation
        with torch.no_grad():
            max_next_q_values = self.target_net(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * max_next_q_values * (1 - dones))

        # 3. Calculate Loss
        loss = self.criterion(q_values, target_q_values)

        # 4. Backpropagation & Optimization
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()

    def update_target_network(self):
        """Syncs the target network weights with the policy network."""
        self.target_net.load_state_dict(self.policy_net.state_dict())

    def save(self, file_name='model.pth'):
            model_folder_path = './model'
            # Create the model folder if it doesn't exist
            if not os.path.exists(model_folder_path):
                os.makedirs(model_folder_path)
            
            file_name = os.path.join(model_folder_path, file_name)
            # Save the policy net weights
            torch.save(self.policy_net.state_dict(), file_name)
            print(f"Model saved to {file_name}")
    
    def load(self, file_name='model.pth'):
        model_folder_path = './model'
        file_path = os.path.join(model_folder_path, file_name)
        
        if os.path.exists(file_path):
            self.policy_net.load_state_dict(torch.load(file_path))
            self.target_net.load_state_dict(torch.load(file_path))
            self.policy_net.eval()
            self.target_net.eval() # Returns Q-values, e.g., tensor([1.2, -0.4, 0.8])