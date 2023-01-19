from time import sleep
import pygame
import pygame_menu
from pygame_menu import themes
import sys
import os
import sqlite3


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


pygame.init()
surface = pygame.display.set_mode((600, 400))
on_off = True


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


Registration = pygame_menu.Menu('Registration', 600, 400, theme=themes.THEME_SOLARIZED)
name1 = Registration.add.text_input('Name: ', default='')
password1 = Registration.add.text_input('Password: ', default='')
Registration.add.button('Sign up', action=sign_up)
Registration.add.button('Quit', action=pygame_menu.events.EXIT)


def set_difficulty(value, difficulty):
    print(value)
    print(difficulty)


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
        ErrorWindow1 = pygame_menu.Menu('Autorization', 400, 200, theme=themes.THEME_BLUE)
        ErrorWindow1.add.label(HELP, max_char=-1, font_size=20)
        Autorization._open(ErrorWindow1)
    else:
        on_off = False


Autorization = pygame_menu.Menu('Autorization', 600, 400, theme=themes.THEME_SOLARIZED, onclose=sign_in)
name = Autorization.add.text_input('Name: ', default='')
password = Autorization.add.text_input('Password: ', default='')
Autorization.add.button('Registration', action=registration)
Autorization.add.button('Sign in', action=sign_in)
update_loading = pygame.USEREVENT
arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15))
Autorization.add.button('Quit', action=pygame_menu.events.EXIT)

while on_off:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            exit()
    if Autorization.is_enabled():
        Autorization.update(events)
        Autorization.draw(surface)
        if (Autorization.get_current().get_selected_widget()):
            arrow.draw(surface, Autorization.get_current().get_selected_widget())
    pygame.display.update()


sc = pygame.display.set_mode((800, 800))
sc.fill((255, 255, 255))
pygame.display.update()
clock = pygame.time.Clock()
FPS = 50
sizes_buttons = []


def Opisanie():
    opis_text = ['Данная игра  реазилована в виде проекта Академии Яндекс.Лицея.',
                 'Суть в том, что вам(герою) надо всех перебить и выиграть бой с главным боссом.',
                 'Удачи вам :)!!!', 'Назад']
    sc.fill((0, 0, 0))
    fon = pygame.transform.scale(load_image('fon1.png'), (800, 800))
    sc.blit(fon, (0, 0))
    font = pygame.font.SysFont('Tahoma', 20)
    text_coord = 50
    s = list()
    for i in range(len(opis_text)):
        string_rendered = font.render(opis_text[i], 1, pygame.Color('green'))
        intro_rect = string_rendered.get_rect()

        text_coord += 20
        intro_rect.top = text_coord
        intro_rect.x = 20
        text_coord += intro_rect.height
        sc.blit(string_rendered, intro_rect)
        if i == 3:
            pygame.draw.rect(sc, 'green', (intro_rect.x - 5, text_coord - 25,
                                           intro_rect.width + 10, intro_rect.height + 5), 5)
            s.append((intro_rect.x - 5, text_coord - 25,
                                  intro_rect.width + 10, intro_rect.height + 5))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if s[0][0] <= pos[0] <= s[0][0] + s[0][2] and s[0][1] <= pos[1] <= s[0][1] + s[0][3]:
                    start_screen()
    print(s)




def button_pressed(event_pos):
    global sizes_buttons
    for i in range(len(sizes_buttons)):
        x, y, width, height = sizes_buttons[i]
        if x <= event_pos[0] <= x + width and y <= event_pos[1] <= y + height:
            return i


def start_screen():
    global sizes_buttons
    intro_text = ["Играть", "", 'Лучшие результаты', '', 'Донат',
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

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                n = button_pressed(pygame.mouse.get_pos())
                if n == 0:
                    pass
                elif n == 1:
                    pass
                elif n == 2:
                    pass
                elif n == 3:
                    Opisanie()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


start_screen()
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            exit()
    pygame.display.flip()

sys.excepthook = except_hook
