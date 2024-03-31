import pygame
import random 
pygame.init()
screen = pygame.display.set_mode([800, 600])

class Hero(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('hero.png').convert_alpha()
        width, height = self.image.get_size()
        self.width = width
        self.height = height
        self.rect = self.image.get_rect()
        self.x = 200
        self.y = 400
        self.score = 0
        self.rect.x = self.x
        self.rect.y = self.y

    def left_walk(self):
        self.x -= 5
        if self.x < 0:
            self.x = 0
    def right_walk(self):
        self.x += 5
        if self.x > 800 - self.width:
            self.x = 800 - self.width

    def get_coin(self, s):
        self.score += s

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('coin.png').convert_alpha()
        width, height = self.image.get_size()
        self.width = width
        self.height = height
        self.rect = self.image.get_rect()
        self.x = random.randint(0, 800)
        self.y = 400
        self.rect.x = self.x
        self.rect.y = self.y

class Background:
    def __init__(self):
        self.image = pygame.image.load('dungeon.png').convert_alpha()
        width, height = self.image.get_size()
        self.width = width
        self.height = height
    
    def draw(self, screen):
        screen.blit(self.image, (0, 0))
        

hero = Hero()
coin_list = [Coin() for i in range(5)]
hero_group = pygame.sprite.Group()
hero_group.add(hero)

coin_group = pygame.sprite.Group()
for coin in coin_list:
    coin_group.add(coin)

background = Background()

while True:
    pygame.time.Clock().tick(60)
    current_time = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        hero.left_walk()
    if keys[pygame.K_RIGHT]:
        hero.right_walk()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    background.draw(screen)
    coin_group.update()
    coin_group.draw(screen)
    hero_group.update()
    hero_group.draw(screen)
    for coin in coin_list:
        if pygame.sprite.collide_rect(hero, coin):
            hero.get_coin(100)
            print('get coin', hero.score)
            coin_group.remove(coin)
            coin_list.remove(coin)

    pygame.display.update()
