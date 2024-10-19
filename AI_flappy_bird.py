import pygame
import os
import random
import neat
import pickle

pygame.init()
pygame.display.set_caption("Flappy Bird")

# ------------- Variables -------------

width, height = 600, 800
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
bird_x = 230
bird_y = 350
STAT_FONT = pygame.font.SysFont("comicsans", 30)
generation = 0

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

    def move(self, birds):
        self.x -= self.VEL
        if (self.passed == False):
            if len(birds) > 0:
                if (birds[0].x - self.x) > 55:
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

        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point = bird_mask.overlap(top_mask, top_offset)

        return bottom_point is not None or top_point is not None 


class Game:
    def __init__(self, genomes, config, draw_red_lines):
        self.networks = []
        self.genoms = []
        self.birds = []
        self.config = config
        self.config_genomes = genomes

        self.gravity = 2  
        self.base = Base(730)
        self.pipes = [Pipe(600)]
        self.score = 0
        self.running = True
        self.PIPE_SPAWN_TIME = 1500 # 1.5s
        self.last_pipe = pygame.time.get_ticks() 
        self.pipe_index = 0
        self.draw_red_lines = draw_red_lines
    
    def create_neural_networks(self):
        for genome_id, genome in self.config_genomes: 
            genome.fitness = 0  

            network = neat.nn.FeedForwardNetwork.create(genome, self.config)
            self.networks.append(network)
            self.birds.append(Bird(bird_x, bird_y))
            self.genoms.append(genome)
            


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()

        if (self.birds and self.pipes):
            if len(self.pipes) > 1 and self.birds[0].x > self.pipes[0].x + 55:
                self.pipe_index = 1

        for x, bird in enumerate(self.birds):
            output = self.networks[x].activate(
                (bird.y, abs(bird.y - self.pipes[self.pipe_index].height), abs(bird.y - self.pipes[self.pipe_index].bottom))
            )

            if output[0] > 0.5:
                bird.jump()

    def update(self):
        if not self.running:
            return
        
        self.pipe_index = 0
        if len(self.birds) > 0 and len(self.pipes) > 1:
            if self.birds[0].x > self.pipes[0].x + 55:
                self.pipe_index = 1  

        birds_to_remove = []
        for x, bird in enumerate(self.birds):
            if bird.y >= 665 or bird.y <= 10:
                self.genoms[x].fitness -= 1
                birds_to_remove.append(x)
            else:
                bird.move(self.gravity)
                self.genoms[x].fitness += 0.1

        for index in sorted(birds_to_remove, reverse=True):
            self.birds.pop(index)
            self.networks.pop(index)
            self.genoms.pop(index)

        self.base.move()
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pipe > self.PIPE_SPAWN_TIME:
            self.pipes.append(Pipe(700))
            self.last_pipe = current_time

        for pipe in self.pipes:
            pipe.move(self.birds)
            for x, bird in enumerate(self.birds):
                if pipe.collide(bird): 
                    self.genoms[x].fitness -= 1
                    birds_to_remove.append(x)

        if self.pipes[self.pipe_index].passed:
            for genome in self.genoms:
                genome.fitness += 5
            self.score += 1 


        for index in sorted(birds_to_remove, reverse=True):
            if index < len(self.birds):  
                self.birds.pop(index)
                self.networks.pop(index)
                self.genoms.pop(index)

        self.pipes = [pipe for pipe in self.pipes if pipe.x + pipe.PIPE_TOP.get_width() >= 0]


    def draw(self, generation):
        if not self.running:
            return

        screen.blit(BG_IMG, (0, 0))  

        for bird in self.birds:
            bird.draw(screen) 

            # Draw red lines
            if self.draw_red_lines:
                pygame.draw.line(screen, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (self.pipes[self.pipe_index].x + self.pipes[self.pipe_index].PIPE_TOP.get_width()/2, self.pipes[self.pipe_index].height), 5)
                pygame.draw.line(screen, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (self.pipes[self.pipe_index].x + self.pipes[self.pipe_index].PIPE_BOTTOM.get_width()/2, self.pipes[self.pipe_index].bottom), 5)

        for pipe in self.pipes:
            pipe.draw(screen)
               

        self.base.draw(screen)

        score_label = STAT_FONT.render("Score: " + str(self.score),1,(255,255,255))
        screen.blit(score_label, (5, 55))

        alive_label = STAT_FONT.render("Alive: " + str(len(self.birds)),1,(255,255,255))
        screen.blit(alive_label, (5, 5))

        generation_label = STAT_FONT.render("Gen: " + str(generation),1,(255,255,255))
        screen.blit(generation_label, (5, 105))

        

        pygame.display.update()  

    def run(self):
        global generation
        generation += 1

        self.create_neural_networks()
        while self.running:  
            clock.tick(35)
            self.handle_events()
            self.update()
            self.draw(generation)

            if len(self.birds) < 1:
                break

            if self.score >= 50: # Save bird if it's really good
                pickle.dump(self.networks[0],open("best.pickle", "wb"))


def eval_genomes(genomes, config):
    game = Game(genomes, config, True) # Draw red lines - True
    game.run()  


# ------------- A.I stuff -------------
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    p = neat.Population(config)


    winner = p.run(eval_genomes, 50)

    print('\nBest genome:\n{!s}'.format(winner))



if __name__ == "__main__":
    local_dir = os.path.dirname((__file__))
    config_path = os.path.join(local_dir, "neat-config.txt")
    run(config_path)