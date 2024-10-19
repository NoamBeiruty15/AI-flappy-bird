import pygame
import os
import random
import neat

pygame.init()
pygame.display.set_caption("Flappy Bird")

# ------------- Variables -------------

width, height = 600, 800
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
bird_x = 230
bird_y = 350
STAT_FONT = pygame.font.SysFont("comicsans", 40)

# ------------- Images -------------
BIRD_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images/bird1.png")).convert_alpha())
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("images", "bg.png")).convert_alpha(), (600, 900))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base.png")).convert_alpha())
PIPE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("images", "pipe.png")).convert_alpha(), (70, 500))

# ------------- Classes -------------

class Bird:
    IMGS = BIRD_IMG
    MAX_ROTATION = 25
    ROT_VEL = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img = self.IMGS
        self.mask = pygame.mask.from_surface(self.img) 
        self.jump_sterngth = 8

    def jump(self):
        self.vel = -(self.jump_sterngth)
        self.tick_count = 0
        self.height = self.y

    def move(self, gravity):
        self.tick_count += 1
        displacement = self.vel * self.tick_count + 0.5 * gravity * (self.tick_count ** 2)

        if displacement >= 16:
            displacement = 16 

        if displacement < 0:
            displacement -= 2

        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return self.mask 


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


class Pipe:
    VERTICAL_GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False

        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.VERTICAL_GAP

    def move(self):
        self.x -= self.VEL
        if (self.passed == False):
            if (bird_x - self.x) > 55:
                self.passed = True

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top)) 
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        return b_point is not None or t_point is not None  


class Game:
    def __init__(self):
        self.gravity = 2 
        self.base = Base(730)
        self.bird = Bird(bird_x, bird_y)
        self.pipes = []
        self.score = 0
        self.running = True
        self.PIPE_SPAWN_TIME = 2000
        self.last_pipe = pygame.time.get_ticks()
        self.paused = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.bird.jump()
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) and self.paused == True:
                game = Game()
                game.run()
                

    def update(self):
        if (self.running == False):
            return
        if (self.paused == False): 
            if self.bird.y >= 665:
                self.bird.y = 665
            elif self.bird.y <= 10:
                self.bird.y = 10             
            self.bird.move(self.gravity)
            self.base.move()

            current_time = pygame.time.get_ticks()
            if current_time - self.last_pipe > self.PIPE_SPAWN_TIME:
                self.pipes.append(Pipe(600))  
                self.last_pipe = current_time

            for pipe in self.pipes:
                pipe.move()
                if ((self.bird.x - pipe.x) > 50) and pipe.passed == False:
                    self.score += 1 
                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    self.pipes.remove(pipe) 
                    

                if pipe.collide(self.bird): 
                    self.paused = True

    def draw(self):
        if (self.running == False):
            return
            
        screen.blit(BG_IMG, (0, 0))  
        self.bird.draw(screen)  
        self.base.draw(screen)  
        for pipe in self.pipes:
            pipe.draw(screen)  

        score_label = STAT_FONT.render("Score: " + str(self.score),1,(255,255,255))
        screen.blit(score_label, (20, 5))
        
        pygame.display.update()

    def run(self):
        while self.running:
            clock.tick(35)  
            self.handle_events()  
            self.update() 
            self.draw()  

        pygame.quit()



if __name__ == "__main__":
    game = Game()
    game.run()  

