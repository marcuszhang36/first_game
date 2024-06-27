import pygame
import random 
from tkinter import Tk, messagebox
pygame.init()
screen = pygame.display.set_mode([800, 600])
class Level:
    def __init__(self, dragon_count, atk, bld, coin, level_id, sublevel_id):
        self.dragon_count = dragon_count
        self.atk = atk
        self.bld = bld
        self.coin = coin
        self.level_id = level_id
        self.sublevel_id = sublevel_id



class Hero(pygame.sprite.Sprite):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('hero.png').convert_alpha()
        width, height = self.image.get_size()
        self.width = width
        self.height = height
        self.rect = self.image.get_rect()
        self.x = 200
        self.dx = 0
        self.y = 400
        self.score = 0
        self.energy = 100
        self.max_energy = 100
        self.attack = 10
        self.can_poison = 0
        self.rect.x = self.x
        self.rect.y = self.y
        self.frame_offset = 0
        self.prev_move = Hero.LEFT

    def reset_dx(self):
        self.dx = 0

    def get_dx(self):
        return self.dx

    def left_walk(self):
        old_x = self.x
        self.x -= 5
        if self.x < self.frame_offset:
            self.x = self.frame_offset
        self.dx += self.x - old_x
    def right_walk(self):
        old_x = self.x
        self.x += 5
        if self.x > self.frame_offset + GameState.WIDTH - self.width:
            self.x = self.frame_offset + GameState.WIDTH - self.width
        self.dx += self.x - old_x
    def up_walk(self):
        self.y -= 5
        if self.y < 35 :
            self.y = 35
    def down_walk(self):
        self.y += 5
        if self.y > 520 - self.height:
            self.y = 520  - self.height
    def get_coin(self, coin):
        if coin.name == "coin":
            self.score += coin.score
        elif coin.name == "egg":
            self.can_poison = 1
        elif coin.name == "life_egg":
            self.energy+=0.1*self.max_energy

    def move(self, op):
        self.prev_move = op
        if op == Hero.DOWN:
            self.down_walk()
        elif op == Hero.UP:
            self.up_walk()
        elif op == Hero.LEFT:
            self.left_walk()
        elif op == Hero.RIGHT:
            self.right_walk()


    def collide(self):
        if self.prev_move == Hero.DOWN:
            self.up_walk()
        elif self.prev_move == Hero.UP:
            self.down_walk()
        elif self.prev_move == Hero.LEFT:
            self.right_walk()
        elif self.prev_move == Hero.RIGHT:
            self.left_walk()

    def update(self):    
        self.rect.x = self.x - self.frame_offset
        self.rect.y = self.y

    def update_frame_offset(self, offset):
        self.frame_offset = offset
    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(screen, (255, 255, 255), (self.rect.x - 8, self.rect.y - 12, self.width + 16, 9))
        x = self.energy/self.max_energy
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x - 8, self.rect.y - 12, x*(self.width + 16), 9))


class Coin(pygame.sprite.Sprite):
    PROB_LIFE_EGG = 0.75
    PROB_POISON_EGG = 0.25
    def __init__(self, x, y, name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        if name == "coin":
            self.image = pygame.image.load('coin.png').convert_alpha()
        elif name == "egg":
            self.image = pygame.image.load('egg.png').convert_alpha()
        elif name == "life_egg":
            self.image = pygame.image.load('life_egg.png').convert_alpha()
        width, height = self.image.get_size()
        self.width = width
        self.height = height
        self.rect = self.image.get_rect()
        self.score = 100
        self.x = x
        self.y = y
        self.rect.x = self.x
        self.rect.y = self.y
        self.frame_offset = 0
        
    def update_frame_offset(self, offset):
        self.frame_offset = offset
        self.rect.x = self.x - self.frame_offset

    def generate(x, y):
        r = random.random()
        if r <= Coin.PROB_LIFE_EGG:
            return Coin(x, y, 'life_egg')
        elif r <= Coin.PROB_LIFE_EGG+Coin.PROB_POISON_EGG:
            return Coin(x, y, 'egg')
        else:
            return None


class Dragon(pygame.sprite.Sprite):
    ASLEEP = 0
    AWAKE = 1
    FLY = 2
    FLY_WAIT_INTERVAL = 5000
    FLY_INTERVAL = 1000
    TIME_INTERVAL = 5000
    POISONED_TIME = 10000
    POISONED_TIME_BLOOD = 1000
    def __init__(self, x, y, energy, attack, coin):
        pygame.sprite.Sprite.__init__(self)
        self.awake_image = pygame.image.load('Dragon-awake.png').convert_alpha()
        self.asleep_image = pygame.image.load('Dragon-asleep.png').convert_alpha()
        self.fly_image = pygame.image.load('Dragon-asleep.png').convert_alpha()
        self.asleep_poisoning_image = pygame.image.load('Dragon-asleep-poisoning.png').convert_alpha()
        self.awake_poisoning_image = pygame.image.load('Dragon-awake-poisoning.png').convert_alpha()
        self.state = Dragon.FLY
        self.is_poisoned = 0
        self.poisoned_time = 0
        self.begin_time = pygame.time.get_ticks()
        self.endx = x
        self.endy = y
        self.x = x
        self.y = 0
        self.energy = energy
        self.max_energy = energy
        self.attack = attack
        self.frame_offset = 0
        self.coin = coin
        self.asleep()
    
    def attackable_rect(self):
        return pygame.Rect(self.rect.x - 10, self.rect.y - 10, self.rect.width + 20, self.rect.height + 20)
    
    def update_rect(self):
        width, height = self.image.get_size()
        self.width = width
        self.height = height
        self.rect = self.image.get_rect()
        self.rect.x = self.x - width - self.frame_offset
        self.rect.y = self.y - height


    def awake(self):
        self.image = self.awake_image
        if self.is_poisoned:
            self.image = self.awake_poisoning_image
        self.update_rect()

    def asleep(self):
        self.image = self.asleep_image
        if self.is_poisoned:
            self.image = self.asleep_poisoning_image
        self.update_rect()

    def fly(self):
        self.image = self.fly_image
        self.update_rect()
    
    def poisoned(self):
        self.poisoned_time = pygame.time.get_ticks()
        self.is_poisoned = 1
    
    def attacked(self, attack, can_poison):
        self.energy-=attack
        if can_poison == 1:
            self.poisoned()
    
    def update(self):
        cur_time = pygame.time.get_ticks()
        if cur_time-self.poisoned_time >= Dragon.POISONED_TIME and self.is_poisoned == 1:
            self.is_poisoned = 0
        if self.is_poisoned == 1:
            self.energy-=Dragon.POISONED_TIME_BLOOD/Dragon.POISONED_TIME*(1000/60)
        if self.state == Dragon.FLY:
            if cur_time-self.begin_time>=Dragon.FLY_WAIT_INTERVAL:
                V = self.endy/Dragon.FLY_INTERVAL
                self.y+=V*(1000/60)
                if self.y>=self.endy:
                    self.y = self.endy
                    self.state = Dragon.ASLEEP
                    self.asleep()
                else:
                    self.fly()

        elif cur_time - self.begin_time > Dragon.TIME_INTERVAL:
            self.begin_time = cur_time
            if self.state == Dragon.ASLEEP:
                self.state = Dragon.AWAKE
                self.awake()
            elif self.state == Dragon.AWAKE:
                self.state = Dragon.ASLEEP
                self.asleep()
        else:
            if self.state == Dragon.ASLEEP:
                self.asleep()
            elif self.state == Dragon.AWAKE:
                self.awake()
    def update_frame_offset(self, offset):
        self.rect.x = self.rect.x + self.frame_offset - offset
        self.frame_offset = offset
    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        x, y = self.x - self.frame_offset- self.awake_image.get_width() - 8, self.y - self.awake_image.get_height() - 12
        pygame.draw.rect(screen, (255, 255, 255), (x, y, self.awake_image.get_width() + 16, 9))
        p = self.energy/self.max_energy
        pygame.draw.rect(screen, (255, 0, 0), (x, y, p*(self.awake_image.get_width() + 16), 9))

class GameState:
    WIDTH = 800
    HEIGHT = 600
    def __init__(self):
        self.levels = []
        self.levels.append(Level(1, 1, 5000, 3, 0, 0))
        self.levels.append(Level(2, 3, 1000, 5, 0, 1))
        self.levels.append(Level(3, 3, 2000, 7, 1, 0))
        self.levels.append(Level(3, 3, 3000, 4, 2, 0))
        self.levels.append(Level(3, 3, 4000, 5, 3, 0))
        self.levels.append(Level(3, 3, 4000, 5, 3, 0))
        self.levels.append(Level(3, 3, 4000, 6, 3, 9))
        self.levels.append(Level(3, 3, 4000, 5, 6, 0))
        self.current_level_index = 0
        self.current_level = 0 
        self.frame_offset = 0
    
    def gen_dragon_list(self) -> list:
        dragon_list = []
        level = self.levels[self.current_level_index]
        for i in range(level.dragon_count):
            dragon_list.append(Dragon((self.current_level+1)*GameState.WIDTH, 150 * (i + 1) + 50, level.bld, level.atk, level.coin))
        return dragon_list
    
    def next_level(self):
        self.current_level_index += 1
        if not self.is_last_level():
            self.current_level = self.levels[self.current_level_index].level_id
    
    def update_frame_offset(self, delta):
        delta = max(delta, 0)
        self.frame_offset = min(self.frame_offset + delta, GameState.WIDTH * self.current_level)
    
    def is_last_level(self):
        return self.current_level_index == len(self.levels) - 1
             

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, can_poison):
        pygame.sprite.Sprite.__init__(self)
        if can_poison == 1:
            self.image = pygame.image.load('poison-fireball.png').convert_alpha()
        else:
            self.image = pygame.image.load('fireball.png').convert_alpha()
        width, height = self.image.get_size()
        self.width = width
        self.height = height
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.can_poison = can_poison
        self.attack = 100
        self.speed = 10
        self.rect.x = x
        self.rect.y = y

        self.frame_offset = 0

    def update(self):
        self.x += self.speed
        self.rect.x = self.x - self.frame_offset

    def update_frame_offset(self, offset):
        self.frame_offset = offset
        self.rect.x = self.x - self.frame_offset

class Background:
    def __init__(self):
        self.image = pygame.image.load('dungeon.png').convert_alpha()
        width, height = self.image.get_size()
        self.width = width
        self.height = height

    def draw(self, screen, offset):
        x = offset % self.width
        screen.blit(self.image, (self.width - x, 0))
        screen.blit(self.image, (-x, 0))

def explode_coin(lx, ly, rx, ry, cnt):
    explode_coin_list = []
    for i in range(cnt):
        x = random.uniform(lx, rx)
        y = random.uniform(ly, ry)    
        explode_coin_list.append(Coin(x, y, "coin"))
    x = random.uniform(lx, rx)
    y = random.uniform(ly, ry)
    explode_coin_list.append(Coin.generate(x, y))
    return explode_coin_list


def popup(message):
    Tk().wm_withdraw()
    messagebox.showinfo('Game information', message)

gstate = GameState()

hero = Hero()
coin_list = []
hero_group = pygame.sprite.Group()
hero_group.add(hero)

coin_group = pygame.sprite.Group()
for coin in coin_list:
    coin_group.add(coin)
arrow_list = []
arrow_group = pygame.sprite.Group()
dragon_group = pygame.sprite.Group()
dragon_list = gstate.gen_dragon_list()
for dragon in dragon_list:
    dragon_group.add(dragon)
background = Background()

pygame.key.stop_text_input()
pygame.mixer.Channel(0).play(pygame.mixer.Sound("bgm.ogg"), -1)

while True:
    pygame.time.Clock().tick(60)
    current_time = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()
    hero.reset_dx()
    if keys[pygame.K_LEFT]:
        hero.move(Hero.LEFT)
    if keys[pygame.K_RIGHT]:
        hero.move(Hero.RIGHT)
    if keys[pygame.K_UP]:
        hero.move(Hero.UP)
    if keys[pygame.K_DOWN]:
        hero.move(Hero.DOWN)
    if keys[pygame.K_SPACE]:
        for dragon in dragon_list:
            if pygame.Rect.colliderect(hero.rect, dragon.attackable_rect()):
                if dragon.state == Dragon.ASLEEP:
                    dragon.attacked(hero.attack, hero.can_poison)
                    print(dragon.energy)

    
    if len(dragon_list) == 0:
        print(f'Level {gstate.current_level} clear!')
        if gstate.is_last_level():
            print('Game clear!')
            popup('Game clear!')
            break
        gstate.next_level()
        dlist = gstate.gen_dragon_list()
        dragon_list += dlist
        for n in dlist:
            dragon_group.add(n)
    

    for dragon in dragon_list:
         if pygame.sprite.collide_rect(hero, dragon):
            if dragon.state == Dragon.AWAKE:
                hero.energy-=dragon.attack
            hero.collide()

    # 用上次hero的移动量来更新frame offset
    gstate.update_frame_offset(hero.get_dx())
    # 更新所有东西的frame offset
    hero.update_frame_offset(gstate.frame_offset)
    for dragon in dragon_list:
        dragon.update_frame_offset(gstate.frame_offset)
    for coin in coin_list:
        coin.update_frame_offset(gstate.frame_offset)
    for arrow in arrow_list:
        arrow.update_frame_offset(gstate.frame_offset)    
    
    if hero.energy<=0:
        hero_group.remove(hero)
    
    for dragon in dragon_list:
        if dragon.energy <= 0:
            dragon_list.remove(dragon)
            dragon_group.remove(dragon)
            coins = explode_coin(dragon.x-dragon.width, dragon.y-dragon.height, dragon.x, dragon.y, dragon.coin)
            #pygame.mixer.Channel(1).play(pygame.mixer.Sound("dragon_dead.ogg"), 0, 1000)
            for coin in coins:
                coin.update_frame_offset(gstate.frame_offset)
                coin_list.append(coin)
                coin_group.add(coin)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_s:
                can_posion = 0
                if event.key == pygame.K_a:
                    can_poison = 0
                if event.key == pygame.K_s and hero.can_poison == 1:
                    can_posion = 1
                arrow = Arrow(hero.x + hero.width,hero.y + hero.height*0.5, can_posion)
                arrow.update_frame_offset(gstate.frame_offset)
                arrow_list.append(arrow)
                arrow_group.add(arrow)
            

    background.draw(screen, gstate.frame_offset)
    arrow_group.update()
    arrow_group.draw(screen)
    coin_group.update()
    coin_group.draw(screen)
    hero_group.update()
    for hero in hero_group:
        hero.draw(screen)
    dragon_group.update()
    for dragon in dragon_group:
        dragon.draw(screen)
    for coin in coin_list:
        if pygame.sprite.collide_rect(hero, coin):

            hero.get_coin(coin)
            print('get coin', hero.score)
            coin_group.remove(coin)
            coin_list.remove(coin)
    
    for dragon in dragon_list:
        for arrow in arrow_list:
            if pygame.sprite.collide_rect(dragon, arrow):
                dragon.attacked(arrow.attack, arrow.can_poison)
                arrow_group.remove(arrow)
                arrow_list.remove(arrow)

    for arrow in arrow_list:
        if arrow.rect.x > 800:
            arrow_group.remove(arrow)
            arrow_list.remove(arrow)

    pygame.display.update() 
