from src.game import AI
from src.agent import Agent
from src.helper import plot

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    
    agent = Agent()
    game = AI(render=False)
    
    while True:
        old_state = agent.get_state(game)
        final_action = agent.get_action(old_state)
        reward, done, score = game.playStep(final_action)
        new_state = agent.get_state(game)
        agent.train_short_memory(old_state, new_state, final_action, reward, done)
        agent.remember(old_state, new_state, final_action, reward, done)
        
        if done:
            print(game.iter)
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.trainer.save()
                
            print(f'Game {agent.n_games} | Score {score} | Record {record}')

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()