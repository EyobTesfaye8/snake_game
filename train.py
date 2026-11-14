import random
import numpy as np
from collections import deque
from src.game import AI
from src.agent import Agent
from src.helper import plot

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    
    agent = Agent()
    game = AI()
    
    while True:
        # old_state, new_state, action, reward, gameover
        # 1. Get current state
        old_state = agent.get_state(game)
        
        # 2. Get move (decide between explore/exploit)
        final_action = agent.get_action(old_state)
        
        # 3. Perform move in the game environment
        reward, done, score = game.playStep(final_action)
        
        # 4. Get the new state
        new_state = agent.get_state(game)
        
        # 5. Train short-term memory (this single step)
        agent.train_short_memory(old_state, new_state, final_action, reward, done)
        
        # 6. Remember this transition in the replay buffer
        agent.remember(old_state, new_state, final_action, reward, done)
        
        if done:
            # Game over: reset game, increment game counter, train long-term memory
            game.reset()
            agent.n_games += 1
            
            # Train long-term memory (Experience Replay batch)
            agent.train_long_memory()
            
            # Save if it's a new high score
            if score > record:
                record = score
                # agent.trainer.policy_net.save() # Uncomment if you want to save weights to model/model.pth
                
            print(f'Game {agent.n_games} | Score {score} | Record {record}')
            
            # Update plotting data
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()