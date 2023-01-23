import pygame
import os
import sys
import pygame_menu
from pygame_menu import themes
import time
from datetime import timedelta
import sqlite3


#parser = argparse.ArgumentParser()
#parser.add_argument("map", type=str, nargs="?", default="map.map")
#args = parser.parse_args()
map_file = 'project1 (1).txt'


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
screen_size = (600, 400)
screen = pygame.display.set_mode(screen_size)
FPS = 50


on_off = True


def sign_up():
    global name1, password1, on_off
    con = sqlite3.connect('Soul.db')
    cur = con.cursor()
    result = cur.execute("SELECT Nickname FROM Registration").fetchall()
    log_pass = [result[i][0] for i in range(len(result))]
    if name1.get_value() in log_pass:
        HELP = "Такой ник уже занят, попробуйте другой"
        ErrorWindow2 = pygame_menu.Menu('Registration', 400, 200, theme=themes.THEME_BLUE)
        ErrorWindow2.add.label(HELP, max_char=-1, font_size=20)
        Registration._open(ErrorWindow2)
    elif len(password1.get_value()) < 6:
        HELP = "Такой пароль слишком короткий, попробуйте другой"
        ErrorWindow3 = pygame_menu.Menu('Registration', 400, 200, theme=themes.THEME_BLUE)
        ErrorWindow3.add.label(HELP, max_char=-1, font_size=20)
        Registration._open(ErrorWindow3)
    else:
        cur.execute('''INSERT INTO Registration(Nickname, Password)
                         VALUES(?, ?)''', (name1.get_value(), password1.get_value()))
        con.commit()
        cur.close()
        on_off = False


Registration = pygame_menu.Menu('Регистрация', 600, 400, theme=themes.THEME_SOLARIZED)
name1 = Registration.add.text_input('Ник: ', default='')
password1 = Registration.add.text_input('Пароль: ', default='')
Registration.add.button('Зарегистрироваться', action=sign_up)
Registration.add.button('Выйти', action=pygame_menu.events.EXIT)


def registration():
    Autorization._open(Registration)
    pygame.time.set_timer(update_loading, 30)


def sign_in():
    global name, password, on_off
    con = sqlite3.connect('Soul.db')
    cur = con.cursor()
    result = cur.execute("SELECT Nickname, Password FROM Registration WHERE Nickname = ? AND Password = ?",
                         (name.get_value(), password.get_value())).fetchone()
    con.close()
    if result is None:
        HELP = "Возможно вы ввели некорректный ник или пароль"
        ErrorWindow1 = pygame_menu.Menu('Авторизация', 400, 200, theme=themes.THEME_BLUE)
        ErrorWindow1.add.label(HELP, max_char=-1, font_size=20)
        Autorization._open(ErrorWindow1)
    else:
        on_off = False


Autorization = pygame_menu.Menu('Авторизация', 600, 400, theme=themes.THEME_SOLARIZED, onclose=sign_in)
name = Autorization.add.text_input('Ник: ', default='')
password = Autorization.add.text_input('Пароль: ', default='')
Autorization.add.button('Регистрация', action=registration)
Autorization.add.button('Войти', action=sign_in)
update_loading = pygame.USEREVENT
arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15))
Autorization.add.button('Выход', action=pygame_menu.events.EXIT)

while on_off:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if Autorization.is_enabled():
        Autorization.update(events)
        Autorization.draw(screen)
        if (Autorization.get_current().get_selected_widget()):
            arrow.draw(screen, Autorization.get_current().get_selected_widget())
    pygame.display.flip()


screen_size = (800, 800)
screen = pygame.display.set_mode(screen_size)
kills = 0
kills_on_level = 0
n_enemies = 0
tel_x, tel_y = 0, 0
priz_x, priz_y = 0, 0
next_level = False
is_dead_boss = False
is_pobeda = False

tile_width = tile_height = 50

tile_images = {
    'wall': pygame.transform.scale(load_image('stena.jpg'), (tile_width, tile_height)),
    'empty': pygame.transform.scale(load_image('земля.jpg'), (tile_width, tile_height)),
    'pol': pygame.transform.scale(load_image('pol.jpg'), (tile_width, tile_height)),
    'door': pygame.transform.scale(load_image('door.png'), (tile_width, tile_height)),
    'enemy': pygame.transform.scale(load_image('крот2.png'), (tile_width, tile_height)),
    'teleport': pygame.transform.scale(load_image('teleport.jpg'), (tile_width, tile_height)),
    'lava': pygame.transform.scale(load_image('lava.jpg'), (tile_width, tile_height)),
    'boss': pygame.transform.scale(load_image('boss.png'), (tile_width, tile_height)),
    'priz': pygame.transform.scale(load_image('priz.png'), (tile_width, tile_height))
}
player_image = pygame.transform.scale(load_image('заяц.png'), (tile_width, tile_height))

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


class Barrier(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.add(barrier_group)
        self.pos = (pos_x, pos_y)


class Priz(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.add(priz_group)
        self.pos = (pos_x, pos_y)


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


class BossEnemy(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.add(bossenemy_group)


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
            tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        global kills, kills_on_level, next_level, is_dead_boss, is_pobeda
        a = len(enemy_group)
        if pygame.sprite.spritecollideany(self, teleport_group):
            next_level = True
        if pygame.sprite.spritecollide(self, enemy_group, True):
            b = len(enemy_group)
            if a != b:
                kills += 1
                kills_on_level += 1
        if pygame.sprite.spritecollide(self, bossenemy_group, True):
            is_dead_boss = True
        if pygame.sprite.spritecollide(self, priz_group, True):
            is_pobeda = True
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
barrier_group = pygame.sprite.Group()
bossenemy_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()
priz_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit


sc = pygame.display.set_mode((800, 800))
sc.fill((255, 255, 255))
pygame.display.update()
sizes_buttons = []
is_game = False
is_results = False
is_start_screen = False
is_about_game = False
is_death = False


def Opisanie():
    global is_about_game, is_game, is_results, is_start_screen
    opis_text = ['Данная игра  реазилована в виде проекта Академии Яндекс.Лицея.',
                 'Суть в том, что вам(герою) надо всех перебить и выиграть бой с главным боссом.',
                 'Удачи вам :)!!!', 'Чтобы вернутся назад, нажмите ESC']
    sc.fill((0, 0, 0))
    fon = pygame.transform.scale(load_image('fon1.png'), (800, 800))
    sc.blit(fon, (0, 0))
    font = pygame.font.SysFont('Tahoma', 20)
    text_coord = 50
    for i in range(len(opis_text)):
        string_rendered = font.render(opis_text[i], 1, pygame.Color('green'))
        intro_rect = string_rendered.get_rect()

        text_coord += 20
        intro_rect.top = text_coord
        intro_rect.x = 20
        text_coord += intro_rect.height
        sc.blit(string_rendered, intro_rect)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_about_game = False
                    is_results = False
                    is_game = False
                    is_start_screen = True
                    return
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()



def button_pressed(event_pos):
    global sizes_buttons
    for i in range(len(sizes_buttons)):
        x, y, width, height = sizes_buttons[i]
        if x <= event_pos[0] <= x + width and y <= event_pos[1] <= y + height:
            return i


def start_screen():
    global sizes_buttons, is_about_game, is_game, is_results, is_start_screen
    screen_size = (800, 800)
    screen = pygame.display.set_mode(screen_size)
    intro_text = ["Играть", "", 'Лучшие результаты', '', '',
                  "",
                  "Об игре"]

    fon = pygame.transform.scale(load_image('fon1.png'), (800, 800))
    sc.blit(fon, (0, 0))
    font = pygame.font.SysFont('Tahoma', 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('green'))
        intro_rect = string_rendered.get_rect()

        text_coord += 20
        intro_rect.top = text_coord
        intro_rect.x = 20
        text_coord += intro_rect.height
        sc.blit(string_rendered, intro_rect)
        if intro_rect.width != 0:
            pygame.draw.rect(sc, 'green', (intro_rect.x - 5, text_coord - 35,
                                           intro_rect.width + 10, intro_rect.height + 5), 5)
            sizes_buttons.append((intro_rect.x - 5, text_coord - 35,
                                 intro_rect.width + 10, intro_rect.height + 5))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                n = button_pressed(pygame.mouse.get_pos())
                if n == 0:
                    is_about_game = False
                    is_results = False
                    is_game = True
                    is_start_screen = False
                    return
                elif n == 1:
                    is_about_game = False
                    is_results = True
                    is_game = False
                    is_start_screen = False
                    return
                elif n == 2:
                    is_about_game = True
                    is_results = False
                    is_game = False
                    is_start_screen = False
                    return
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


def death():
    global is_about_game, is_game, is_results, is_start_screen
    screen_size = (600, 600)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Гибель персонажа')
    fon = pygame.transform.scale(load_image('fon1.png'), screen_size)
    screen.blit((fon), (0, 0))

    font = pygame.font.Font(None, 35)
    text = font.render('Вы погибли', 1, 'red')
    text_x = 100
    text_y = 100
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, 'red', (text_x - 10, text_y - 10, text_w + 20,
                                     text_h + 20), 5)
    text2 = font.render('Нажмите "ESC" чтобы выйти в меню', 1, 'white')
    text_x2 = 50
    text_y2 = 50
    screen.blit(text2, (text_x2, text_y2))

    while True:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_about_game = False
                    is_results = False
                    is_game = False
                    is_start_screen = True
                    return
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


def pobeda():
    global is_about_game, is_game, is_results, is_start_screen
    pygame.display.set_caption('Гибель персонажа')
    screen_size = (600, 600)
    screen = pygame.display.set_mode(screen_size)
    fon = pygame.transform.scale(load_image('fon1.png'), screen_size)
    screen.blit((fon), (0, 0))

    font = pygame.font.Font(None, 35)
    text = font.render('Вы победили, раздавив всех кротов', 1, 'red')
    text_x = 100
    text_y = 100
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, 'red', (text_x - 10, text_y - 10, text_w + 20,
                                     text_h + 20), 5)
    text2 = font.render('Нажмите "ESC" чтобы выйти в меню', 1, 'white')
    text_x2 = 50
    text_y2 = 50
    screen.blit(text2, (text_x2, text_y2))

    while True:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_about_game = False
                    is_results = False
                    is_game = False
                    is_start_screen = True
                    return
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, ' ')), level_map))


def generate_level(level):
    global n_enemies, tel_x, tel_y, priz_x, priz_y
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
            elif level[y][x] == '%':
                Barrier('lava', x, y)
            elif level[y][x] == '~':
                tel_x, tel_y = x, y
            elif level[y][x] == '!':
                Tile('empty', x, y)
                priz_x, priz_y = x, y

    return new_player, x, y


def move(hero, movement):
    global is_death
    x, y = hero.pos
    if movement == "up":
        if y > 0 and level_map[y - 1][x] in [".", ",", "|", "~", '%', '!']:
            if level_map[y - 1][x] == '%':
                is_death = True
            hero.move(x, y - 1)
    elif movement == "down":
        if y < max_y and level_map[y + 1][x] in [".", ",", "|", "~", '%', '!']:
            if level_map[y + 1][x] == '%':
                is_death = True
            hero.move(x, y + 1)
    elif movement == "left":
        if x > 0 and level_map[y][x - 1] in [".", ",", "|", "~", '%', '!']:
            if level_map[y][x - 1] == '%':
                is_death = True
            hero.move(x - 1, y)
    elif movement == "right":
        if x < max_x and level_map[y][x + 1] in [".", ",", "|", "~", '%', '!']:
            if level_map[y][x + 1] == '%':
                is_death = True
            hero.move(x + 1, y)
start_screen()
level_map = load_level(map_file)
hero, max_x, max_y = generate_level(level_map)
camera = Camera(hero)
camera.update(hero)
f = 0
while running:
    if is_start_screen:
        start_screen()
    if is_about_game:
        Opisanie()
    if is_results:
        pass
    if is_game:
        screen_size = (600, 600)
        screen = pygame.display.set_mode(screen_size)
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
            if kills_on_level == n_enemies:
                if map_file == 'project2.txt':
                    Tile('empty', tel_x, tel_y)
                    BossEnemy('boss', tel_x, tel_y)
                    f += 1
                else:
                    Teleport('teleport', tel_x, tel_y)
        if next_level:
            teleport_group = pygame.sprite.Group()
            enemy_group = pygame.sprite.Group()
            sprite_group = SpriteGroup()
            hero_group = SpriteGroup()
            n_enemies = 0
            tel_x, tel_y = 0, 0
            screen.fill((0, 0, 0))
            map_file = 'project2.txt'
            level_map = load_level(map_file)
            hero, max_x, max_y = generate_level(level_map)
            camera = Camera(hero)
            camera.update(hero)
            f = 0
            next_level = False
            kills_on_level = 0
        if is_death:
            teleport_group = pygame.sprite.Group()
            enemy_group = pygame.sprite.Group()
            sprite_group = SpriteGroup()
            hero_group = SpriteGroup()
            n_enemies = 0
            tel_x, tel_y = 0, 0
            screen.fill((0, 0, 0))
            map_file = 'project1 (1).txt'
            level_map = load_level(map_file)
            hero, max_x, max_y = generate_level(level_map)
            camera = Camera(hero)
            camera.update(hero)
            f = 0
            next_level = False
            kills_on_level = 0
            kills = 0
            is_death = False
            is_dead_boss = False
            is_pobeda = False
            priz_x, priz_y = 0, 0
            death()
        if is_dead_boss:
            Priz('priz', priz_x, priz_y)
        if is_pobeda:
            pobeda()
        screen.fill(pygame.Color("black"))
        sprite_group.draw(screen)
        teleport_group.draw(screen)
        enemy_group.draw(screen)
        hero_group.draw(screen)
        bossenemy_group.draw(screen)
        priz_group.draw(screen)
        sprite_group.update()
        clock.tick(FPS)
        pygame.display.flip()
        pygame.time.delay(20)
pygame.quit()
