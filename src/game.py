import sys
import pygame
import random
from pygame.math import Vector2 as V

CELL_SIZE = 30
CELL_NUMBER = 50
WIDTH = HEIGHT = CELL_NUMBER * CELL_SIZE
class Segment(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        # print(type)
        if type == "hd":
            img = pygame.image.load("assets/head_down.png").convert_alpha()
        elif type == "hu":
            img = pygame.image.load("assets/head_up.png").convert_alpha()
        elif type == "hr":
            img = pygame.image.load("assets/head_right.png").convert_alpha()
        elif type == "hl":
            img = pygame.image.load("assets/head_left.png").convert_alpha()
        elif type == "tu":
            img = pygame.image.load("assets/tail_up.png").convert_alpha()
        elif type == "td":
            img = pygame.image.load("assets/tail_down.png").convert_alpha()
        elif type == "tr":
            img = pygame.image.load("assets/tail_right.png").convert_alpha()
        elif type == "tl":
            img = pygame.image.load("assets/tail_left.png").convert_alpha()
        elif type == "btr":
            img = pygame.image.load("assets/body_topright.png").convert_alpha()
        elif type == "btl":
            img = pygame.image.load("assets/body_topleft.png").convert_alpha()
        elif type == "bbr":
            img = pygame.image.load("assets/body_bottomright.png").convert_alpha()
        elif type == "bbl":
            img = pygame.image.load("assets/body_bottomleft.png").convert_alpha()
        elif type == "bh":
            img = pygame.image.load("assets/body_horizontal.png").convert_alpha()
        elif type == "bv":
            img = pygame.image.load("assets/body_vertical.png").convert_alpha()
        self.x = x * CELL_SIZE
        self.y = y * CELL_SIZE
        self.image = pygame.transform.scale(img, (CELL_SIZE,CELL_SIZE))
        self.rect = self.image.get_rect()
        self.pos = V(self.x, self.y)
        self.rect.center = self.pos

class Snake(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.body = [V(30, 30), V(30,31), V(30,32)]
        self.dirc = V(1,0)
        self.growing = False

        self.sprites = pygame.sprite.Group()
        self.rebuild()

    def rebuild(self):
        self.sprites.empty()
        for i, pos in enumerate(self.body):
            if i == 0:
                type = self.getType(self.body[i + 1], pos, None, i)
            elif len(self.body)-1 == i:
                type = self.getType(None, pos, self.body[i - 1], -1)
            else: 
                type = self.getType(self.body[i+1], pos, self.body[i-1], 1)
            segment = Segment(pos[0], pos[1], type)
            self.sprites.add(segment)
        
    def update(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.dirc
        new_head = V(head_x + dir_x, head_y + dir_y)

        self.body.insert(0, new_head)

        if not self.growing:
            self.body.pop()
        else:
            self.growing = False

        self.rebuild()
    
    def getType(self, back, current, next, i):
        type = "No Type"
        if i == 0:
            dirc = current - back
            if dirc == V(1,0): type = "hr"
            elif dirc == V(-1,0): type = "hl"
            elif dirc == V(0,1): type = "hd"
            elif dirc == V(0,-1): type = "hu"
        elif i == -1:
            dirc = next - current
            if dirc == V(1,0): type = "tl"
            elif dirc == V(-1,0): type = "tr"
            elif dirc == V(0,1): type = "tu"
            elif dirc == V(0,-1): type = "td"
        else:
            dirc_before = current - back
            dirc_after = next - current

            if dirc_before == V(1,0):
                if dirc_after == V(0,1): type = "bbl"
                elif dirc_after == V(0,-1): type = "btl"
            elif dirc_before == V(-1,0):
                if dirc_after == V(0,1): type = "bbr"
                elif dirc_after == V(0,-1): type = "btr"
            elif dirc_before == V(0,1):
                if dirc_after == V(1,0): type = "btr"
                elif dirc_after == V(-1,0): type = "btl"
            elif dirc_before == V(0,-1):
                if dirc_after == V(1,0): type = "bbr"
                elif dirc_after == V(-1,0): type = "bbl"
            if (dirc_after == V(1,0) and dirc_before == V(1,0)) or (dirc_after == V(-1,0) and dirc_before == V(-1,0)): 
                type = "bh"
            elif type == "No Type": type = "bv"
        return type

    def checkCollision(self):
        h = self.body[0]
        if h.x < 0 or h.x > CELL_NUMBER or h.y < 0 or h.y > CELL_NUMBER:
            return True
        if h in self.body[1:]:
            return True
        return False

    def change_direction(self, new_dir):
        if (new_dir[0] != -self.dirc[0] and new_dir[1] != -self.dirc[1]):
            self.dirc = new_dir
    
    def act(self, action):
        if action == "straight":
            pass
        elif action == "right":
            self.dirc = self.dirc.rotate(90)
        elif action == "left":
            self.dirc = self.dirc.rotate(-90)
class Apple(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.spawn()
    def spawn(self):
        self.x = random.randint(0, CELL_NUMBER - 1) * CELL_SIZE
        self.y = random.randint(0, CELL_NUMBER - 1) * CELL_SIZE
        self.pos = V(self.x,self.y)
        image = pygame.image.load("assets/apple.png").convert_alpha()
        self.image = pygame.transform.scale(image, (CELL_SIZE,CELL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

def check_eat(firut, head):
    if head*CELL_SIZE == firut.pos:
        firut.spawn()
        return True
    return False


pygame.init()
screen = pygame.display.set_mode((HEIGHT, WIDTH))
clock = pygame.time.Clock()
firut = Apple()
snake = Snake()

gameOver = False

sprites = pygame.sprite.Group()
sprites.add(firut)
for s in snake.sprites:
    sprites.add(s)


while True:
    for event in pygame.event.get():
        if event == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                snake.act("left")
            elif event.key == pygame.K_RIGHT:
                snake.act("right")
    snake.update()
    gameOver = snake.checkCollision()
    if check_eat(firut, snake.body[0]):
        snake.growing = True
    if gameOver:
        sprites.empty()
        snake = Snake()
        firut = Apple()
        sprites.add(firut)
        for s in snake.sprites:
            sprites.add(s)
        gameOver = False
    
    sprites.empty()
    sprites.add(firut)
    for s in snake.sprites:
        sprites.add(s)
    screen.fill("#489000")
    sprites.update()
    sprites.draw(screen)
    pygame.display.update()
    clock.tick(15)

