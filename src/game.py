import sys
import pygame
import random
from pygame.math import Vector2 as V

CELL_SIZE = 50
CELL_NUMBER = 30
WIDTH = HEIGHT = CELL_NUMBER * CELL_SIZE
class AI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((HEIGHT, WIDTH))
        self.clock = pygame.time.Clock()
        self.sprites = pygame.sprite.Group()
        self.gameOver = False
        self.reset()
            

    def playStep(self, action):
        reward = 0
        self.iter += 1
        # print(self.iter)
        for event in pygame.event.get():
            if event == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction((1, 0))

        old_position = V(self.snake.body[0].x * CELL_SIZE, self.snake.body[0].y * CELL_SIZE)
        # print(old_position)
        self.snake.act(action) # move snake
        # self.keyMove()
        self.snake.update()

        new_position = V(self.snake.body[0].x * CELL_SIZE, self.snake.body[0].y * CELL_SIZE)

        if self.snake.body[0]*CELL_SIZE == self.firut.pos:
            self.snake.growing = True
            self.score += 1
            reward = 10
            self.firut.spawn()
            self.score_sprite.update_score(self.score)

        if self.snake.checkCollision() or self.iter > 100 * len(self.snake.body):
            self.gameOver = True
            reward = -10
            return reward, self.gameOver, self.score
        
        self.sprites.empty()
        self.sprites.add(self.score_sprite)
        self.sprites.add(self.firut)
        for s in self.snake.sprites:
            self.sprites.add(s)
        
        self.screen.fill("#489000")
        self.sprites.update()
        self.sprites.draw(self.screen)
        pygame.display.update()
        self.clock.tick(180)
        reward += self.rewardByDistance(old_position, new_position)
        # print(reward)

        return reward, self.gameOver, self.score

    def reset(self):
        self.sprites.empty()
        self.score = 0
        self.score_sprite = ScoreSprite(WIDTH - 50, 50)
        self.score_sprite.update_score(self.score)
        self.iter = 0
        self.snake = Snake()
        self.firut = Apple()
        self.sprites.add(self.firut)
        for s in self.snake.sprites:
            self.sprites.add(s)
        self.sprites.add(self.score_sprite)
        self.gameOver = False

    def rewardByDistance(self, old:V, new:V):
        old_distance = abs(old.distance_to(self.firut.pos))
        new_distance = abs(new.distance_to(self.firut.pos))
        # print(new_distance, old_distance)
        if new_distance < old_distance:
            return 0.2
        elif new_distance > old_distance:
            return -0.2
        else: return 0
    def is_collision(pos1, dirc):
        pass

    def get_state(self):
        head = self.snake.body[0] * CELL_SIZE
        firut = self.firut.pos
        
        # danger_s,r,l, moving_r,l,u,d, food_r,l,u,d

        ds = 1 if self.snake.checkCollision(head + self.snake.dirc) else 0
        dr = 1 if self.snake.checkCollision(head + self.snake.dirc.rotate(90)) else 0
        dl = 1 if self.snake.checkCollision(head + self.snake.dirc.rotate(-90)) else 0

        mr = 1 if self.snake.dirc == (1,0) else 0
        ml = 1 if self.snake.dirc == (-1,0) else 0
        md = 1 if self.snake.dirc == (0,1) else 0
        mu = 1 if self.snake.dirc == (0,-1) else 0

        food = firut - head
        fr = 1 if food.x > 0 else 0
        fl = 1 if food.x < 0 else 0
        fu = 1 if food.y < 0 else 0
        fd = 1 if food.y > 0 else 0

        return [ds,dr,dl,mr,ml,md,mu,fr,fl,fu,fd]
    
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
        self.body = [V((CELL_NUMBER // 2), CELL_NUMBER // 2), V((CELL_NUMBER // 2) - 1, CELL_NUMBER // 2), V((CELL_NUMBER // 2) - 2, CELL_NUMBER // 2)]
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

    def checkCollision(self, pos = None):
        if pos: h = pos
        else: h = self.body[0]
        if h.x < 0 or h.x > CELL_NUMBER or h.y < 0 or h.y > CELL_NUMBER:
            return True
        if h in self.body[1:]:
            return True
        return False

    def change_direction(self, new_dir):
        if (new_dir[0] != -self.dirc[0] and new_dir[1] != -self.dirc[1]):
            self.dirc = new_dir
    
    def act(self, action):
        if action == 1:
            self.dirc = self.dirc.rotate(90)
        elif action == 2:
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

class ScoreSprite(pygame.sprite.Sprite):

  def __init__(self, x, y):
    super().__init__()
    self.font = pygame.font.Font(None, 50)
    self.x = x
    self.y = y
    self.update_score(0)  # Initialize with score 0

  def update_score(self, score):
    # Render the text surface
    self.image = self.font.render(f"Score: {score}", False, (255, 255, 255))
    self.rect = self.image.get_rect()
    # Position it at the top-right corner coordinates
    self.rect.topright = (self.x, self.y)

