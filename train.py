import os
import sys
import argparse
from src.game import AI
from src.agent import Agent
from src.helper import plot

def train(render, lr=0.001):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    
    agent = Agent(lr=lr)
    game = AI(render=render)
    
    while True:
        old_state = agent.get_state(game)
        final_action = agent.get_action(old_state)
        reward, done, score = game.playStep(final_action)
        new_state = agent.get_state(game)
        agent.train_short_memory(old_state, new_state, final_action, reward, done)
        agent.remember(old_state, new_state, final_action, reward, done)
        
        if done:
            if not os.path.exists("highscore.txt"):
                file = open("highscore.txt", "x")
                file.write(f"{game.score}")
                file.close()
            else:
                file = open("highscore.txt", "r+")
                highscore = int(file.read().strip())
                if highscore < game.score:
                    file.seek(0)
                    file.truncate(0)
                    file.write(f"{game.score}")
            
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            loss = agent.get_loss()

            if score > record:
                record = score
                agent.trainer.save()
                
            print(f'Game {agent.n_games} | Score {score} | Record {record} | Loss: {loss}')

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train the snake to eat. You can see it as it learns with stastics or just see the numbers.")
    parser.add_argument("-r", action="store_true", help="set rendering the game false (much slower for training the AI)")
    args = parser.parse_args()

    print(f"Render mode enabled: {args.r}")
    train(args.r)