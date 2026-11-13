from src.game import AI
from src.agent import Agent

agent = Agent()
game = AI()

while True:
    reward, gameover, score = game.playStep("straight ")
    if game.gameOver:
        game.reset()