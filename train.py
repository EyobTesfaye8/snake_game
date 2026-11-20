import os
import argparse
from src.game import AI
from src.agent import Agent
from src.helper import plot

PLOT_EVERY = 20   # only redraw plot every N games

def train(render, lr=0.001):
    plot_scores      = []
    plot_mean_scores = []
    total_score      = 0
    record           = 0

    agent = Agent(lr=lr)
    game  = AI(render=render)

    # Compute once before the loop starts
    state = agent.get_state(game)

    while True:
        old_state    = state
        final_action = agent.get_action(old_state)
        reward, done, score = game.playStep(final_action)
        new_state    = agent.get_state(game)
        agent.remember(old_state, new_state, final_action, reward, done)

        state = new_state   # carry forward — no recompute next step

        if done:
            game.reset()
            agent.n_games += 1
            state = agent.get_state(game)   # fresh state after reset

            agent.train_long_memory()       # ← the only training call needed
            loss = agent.get_loss()

            if score > record:
                record = score
                agent.trainer.save()

            # Highscore with proper file handling
            _update_highscore(score)

            print(f'Game {agent.n_games} | Score {score} | Record {record} | Loss: {loss:.4f}')

            plot_scores.append(score)
            total_score += score
            plot_mean_scores.append(total_score / agent.n_games)

            # ✅ only redraw plot every 20 games
            if agent.n_games % PLOT_EVERY == 0:
                plot(plot_scores, plot_mean_scores)


def _update_highscore(score):
    """Read/write highscore with proper file handling."""
    if not os.path.exists("highscore.txt"):
        with open("highscore.txt", "w") as f:
            f.write(str(score))
    else:
        with open("highscore.txt", "r+") as f:
            highscore = int(f.read().strip() or 0)
            if score > highscore:
                f.seek(0)
                f.truncate()
                f.write(str(score))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", action="store_true", help="Enable rendering")
    args = parser.parse_args()
    print(f"Render mode: {args.r}")
    train(args.r)