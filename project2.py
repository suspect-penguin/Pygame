import pygame
import os
import sys
import argparse
from random import choice
import pprint


#parser = argparse.ArgumentParser()
#parser.add_argument("map", type=str, nargs="?", default="map.map")
#args = parser.parse_args()
map_file = 'project2.txt'


def load_image(name, color_key=-1):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
screen_size = (600, 600)
screen = pygame.display.set_mode(screen_size)
FPS = 50
kills = 0
n_enemies = 0
tel_x, tel_y = 0, 0
next_ = False

tile_width = tile_height = 50

tile_images = {
    'wall': pygame.transform.scale(load_image('stena.jpg'), (tile_width, tile_height)),
    'empty': pygame.transform.scale(load_image('земля.jpg'), (tile_width, tile_height)),
    'pol': pygame.transform.scale(load_image('pol.jpg'), (tile_width, tile_height)),
    'door': pygame.transform.scale(load_image('door.png'), (tile_width, tile_height)),
    'enemy': pygame.transform.scale(load_image('крот.png'), (tile_width, tile_height)),
    'teleport': pygame.transform.scale(load_image('teleport.jpg'), (tile_width, tile_height))
}
player_image = load_image('mar.png')

class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)


class Enemy(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.add(enemy_group)
        self.pos = (pos_x, pos_y)

    def move(self, max_x, max_y):
        a = choice([-1, 0, 1])
        b = choice([-1, 0, 1])
        x, y = self.pos
        if 0 <= y + a <= max_y:
            if 0 <= x + b <= max_x:
                if level_map[y + a][x + b] == ',':
                    self.pos = [x + b, y + a]


class Teleport(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.add(teleport_group)
        self.pos = (pos_x, pos_y)


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        global kills, next_
        a = len(enemy_group)
        if pygame.sprite.spritecollideany(self, teleport_group):
            next_ = True
        if pygame.sprite.spritecollide(self, enemy_group, True):
            b = len(enemy_group)
            if a != b:
                kills += 1
        if not pygame.sprite.spritecollide(self, enemy_group, True):
            camera.dx -= tile_width * (x - self.pos[0])
            camera.dy -= tile_height * (y - self.pos[1])
            self.pos = (x, y)
            for sprite in sprite_group:
                camera.apply(sprite)





class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, target):
        self.dx = target.pos[0]
        self.dy = target.pos[1]

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self, target):
        self.dx = target.pos[0]
        self.dy = target.pos[1]


player = None
running = True
clock = pygame.time.Clock()
teleport_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()


def terminate():
    pygame.quit()
    sys.exit


def start_screen():
    intro_text = ["Перемещение героя", "",
                  "",
                  "Камера"]

    fon = pygame.transform.scale(load_image('fon1.png'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.SysFont('Tahoma', 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, ' ')), level_map))


def generate_level(level):
    global n_enemies, tel_x, tel_y
    new_player, x, y, enemies = None, None, None, []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                zn = str()
                if level[y][x] == '.':
                    zn = '.'
                elif level[y][x] == ',':
                    zn = ','
                else:
                    zn = '.'
                if zn == '.':
                    Tile('empty', x, y)
                else:
                    Tile('pol', x, y)
                new_player = Player(x, y)
                level[y][x] = zn
            elif level[y][x] == '|':
                Tile('door', x, y)
            elif level[y][x] == ',':
                Tile('pol', x, y)
            elif level[y][x] == '^':
                Tile('pol', x, y)
                Enemy('enemy', x, y)
                level[y][x] = ','
                n_enemies += 1
            elif level[y][x] == '~':
                tel_x, tel_y = x, y

    return new_player, x, y


def move(hero, movement):
    x, y = hero.pos
    if movement == "up":
        if y > 0 and level_map[y - 1][x] in [".", ",", "|", "~"]:
            hero.move(x, y - 1)
    elif movement == "down":
        if y < max_y and level_map[y + 1][x] in [".", ",", "|", "~"]:
            hero.move(x, y + 1)
    elif movement == "left":
        if x > 0 and level_map[y][x - 1] in [".", ",", "|", "~"]:
            hero.move(x - 1, y)
    elif movement == "right":
        if x < max_x and level_map[y][x + 1] in [".", ",", "|", "~"]:
            hero.move(x + 1, y)


start_screen()
level_map = load_level(map_file)
hero, max_x, max_y = generate_level(level_map)
camera = Camera(hero)
camera.update(hero)
f = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move(hero, "up")
            elif event.key == pygame.K_DOWN:
                move(hero, "down")
            elif event.key == pygame.K_LEFT:
                move(hero, "left")
            elif event.key == pygame.K_RIGHT:
                move(hero, "right")
    if f == 0:
        if kills == n_enemies:
            Teleport('teleport', tel_x, tel_y)
    if next_:
        level_map = load_level('project2.txt')
        hero, max_x, max_y = generate_level(level_map)
        camera = Camera(hero)
        sprite_group = pygame.sprite.Group()
        hero_group = pygame.sprite.Group()
        camera.update(hero)
    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    teleport_group.draw(screen)
    enemy_group.draw(screen)
    hero_group.draw(screen)
    sprite_group.update()
    clock.tick(FPS)
    pygame.display.flip()
    pygame.time.delay(20)
pygame.quit()
