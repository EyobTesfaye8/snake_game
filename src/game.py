import sys
import pygame

class snake(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.img = pygame.image.load("")
    def move():
        pass

    def eat():

CELL_SIZE = 20
CELL_NUMBER = 60

pygame.init()
screen = pygame.display.set_mode((CELL_SIZE*CELL_NUMBER, CELL_SIZE*CELL_NUMBER))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill("#3D7B00")
    pygame.display.update()
    clock.tick(60)

