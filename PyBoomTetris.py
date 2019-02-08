# импорт всех необходимых модулей
import pygame
import random
import os
import sys

pygame.mixer.init()
# Константы и другие необходимые переменные
WIDHT = 850
HEIGHT = 950
TIMER = 1
SPEED = 600
GRAVITY = 0.2
c = 0
screen_rect = (0, 0, WIDHT, HEIGHT)
record = 0
pause = False
pause_color = 'orange'
# Дисплей и таймер для игры
pygame.time.set_timer(TIMER, SPEED)
size = WIDHT, HEIGHT
screen = pygame.display.set_mode(size)
pygame.display.set_caption("PyBoomTetris")
# Загрузка всех фоновых песен и звуков игры
pygame.mixer.music.load('music\privet.wav')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

sound_volume = 0.25
gameover = pygame.mixer.Sound('music\gameover.wav')
gameover.set_volume(sound_volume)
explosion = pygame.mixer.Sound('music\explosion.wav')
explosion.set_volume(sound_volume)
figPlace = pygame.mixer.Sound('music\Place.wav')
figPlace.set_volume(sound_volume)
removeLine = pygame.mixer.Sound('music\RemoveLine.wav')
removeLine.set_volume(1)


# Загрузка картинок для игры
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


# Класс основной доски для тетриса
class Board():
    # создание поля
    def __init__(self, width, height, left=200, top=10, cell_size=50):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.ingame_counter = 0
        self.bomb_counter = 0
        self.bomba = False

    # Создание новой фигуры, если старая установлена(регулируется в осн. коде)
    def figure(self):
        global moving
        # Начальные координаты фигур(9 штук)
        l = [[[0, 5], [0, 4], [0, 6], [1, 6]],  # 0
             [[0, 5], [0, 4], [0, 6], [1, 4]],  # 1
             [[0, 6]],  # 2
             [[0, 5], [0, 6]],  # 3
             [[0, 5], [0, 4], [0, 6]],  # 4
             [[0, 5], [0, 6], [1, 5], [1, 6]],  # 5
             [[1, 5], [0, 5], [1, 4], [0, 6]],  # 6
             [[1, 6], [0, 5], [0, 6], [1, 7]],  # 7
             [[0, 5], [0, 4], [0, 6], [1, 5]]]  # 8
        colors = ['blue', 'yellow', 'red', 'orange', 'green']
        num = random.randint(0, 8)
        self.coords = l[num]
        self.figure_num = num
        self.end = False
        self.color = colors[random.randint(0, 4)]
        moving = True
        for i in range(len(self.coords)):
            if self.board[self.coords[i][0]][self.coords[i][1]] != 0:
                self.end = True
        self.add_to_board()
        self.render()

    # Вспомогательная функция, которая добавит текущую фигуру на поле
    def add_to_board(self):
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = self.color

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # отрисовка поля
    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == 'boom':
                    pygame.draw.rect(
                        screen,
                        pygame.Color('pink'),
                        (self.left + x * self.cell_size, self.top + y * self.cell_size,
                         self.cell_size, self.cell_size),
                    )
                    boom = pygame.transform.scale(load_image('boom.png'), (50, 50))
                    screen.blit(boom, (self.left + x * self.cell_size, self.top + y * self.cell_size))
                elif self.board[y][x] != 0:
                    pygame.draw.rect(
                        screen,
                        pygame.Color(self.board[y][x]),
                        (self.left + x * self.cell_size, self.top + y * self.cell_size,
                         self.cell_size, self.cell_size),
                    )
                pygame.draw.rect(
                    screen,
                    pygame.Color('white'),
                    (self.left + x * self.cell_size, self.top + y * self.cell_size,
                     self.cell_size, self.cell_size),
                    1
                )

    # Проверка пустоты клеток вокруг фигуры для её поворота
    def test_field_around(self, y, x):
        if (x - 1 >= 0 and y - 1 >= 0 and x + 1 < 12 and y + 1 < 18) and \
                (self.board[y - 1][x - 1] == 0 and self.board[y][x - 1] == 0 and
                 self.board[y + 1][x - 1] == 0 and self.board[y - 1][x] == 0 and
                 self.board[y + 1][x] == 0 and self.board[y - 1][x + 1] == 0 and
                 self.board[y][x + 1] == 0 and self.board[y + 1][x + 1] == 0):
            return True
        else:
            return False

    # Функция поворота
    def turn_right(self):
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = 0
        new_coords = [self.coords[0]]
        y, x = self.coords[0]
        if self.test_field_around(y, x):
            if self.figure_num in [0, 1, 4, 6, 7, 8]:
                for i in range(1, len(self.coords)):
                    if self.coords[i][0] == y - 1 and self.coords[i][1] == x - 1:
                        new_coords.append([y - 1, x + 1])
                    if self.coords[i][0] == y - 1 and self.coords[i][1] == x:
                        new_coords.append([y, x + 1])
                    if self.coords[i][0] == y - 1 and self.coords[i][1] == x + 1:
                        new_coords.append([y + 1, x + 1])
                    if self.coords[i][0] == y and self.coords[i][1] == x - 1:
                        new_coords.append([y - 1, x])
                    if self.coords[i][0] == y and self.coords[i][1] == x + 1:
                        new_coords.append([y + 1, x])
                    if self.coords[i][0] == y + 1 and self.coords[i][1] == x - 1:
                        new_coords.append([y - 1, x - 1])
                    if self.coords[i][0] == y + 1 and self.coords[i][1] == x:
                        new_coords.append([y, x - 1])
                    if self.coords[i][0] == y + 1 and self.coords[i][1] == x + 1:
                        new_coords.append([y + 1, x - 1])
            elif self.figure_num == 3:
                if self.coords[1][0] == y - 1 and self.coords[1][1] == x:
                    new_coords.append([y, x + 1])
                if self.coords[1][0] == y and self.coords[1][1] == x + 1:
                    new_coords.append([y + 1, x])
                if self.coords[1][0] == y + 1 and self.coords[1][1] == x:
                    new_coords.append([y, x - 1])
                if self.coords[1][0] == y and self.coords[1][1] == x - 1:
                    new_coords.append([y - 1, x])
            else:
                new_coords = self.coords[:]
            self.coords = new_coords[:]
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = self.color
        self.render()

    # Смещение фигуры налево
    def move_left(self):
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = 0
        f = not (0 in [x[1] for x in self.coords])
        for i in range(len(self.coords)):
            if self.coords[i][1] - 1 >= 0 and \
                    self.board[self.coords[i][0]][self.coords[i][1] - 1] != 0:
                f = False
        if f:
            for i in range(len(self.coords)):
                self.coords[i][1] -= 1
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = self.color

    # Смещение фигуры направо
    def move_right(self):
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = 0
        f = not (self.width - 1 in [x[1] for x in self.coords])
        for i in range(len(self.coords)):
            if self.coords[i][1] + 1 < self.width and \
                    self.board[self.coords[i][0]][self.coords[i][1] + 1] != 0:
                f = False
        if f:
            for i in range(len(self.coords)):
                self.coords[i][1] += 1
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = self.color

    # Смещение фигуры вниз(автоматически, регулируется из осн. кода)
    def move_down(self):
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = 0
        if not (self.height - 1 in [x[0] for x in self.coords]):
            for i in range(len(self.coords)):
                self.coords[i][0] += 1
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = self.color

    # Проверка того, что фигура упёрлась в другую
    def is_stop(self):
        f = False
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = 0
        for i in range(len(self.coords)):
            if self.coords[i][0] + 1 > self.height - 1 or \
                    self.board[self.coords[i][0] + 1][self.coords[i][1]] != 0:
                f = True
        for i in range(len(self.coords)):
            self.board[self.coords[i][0]][self.coords[i][1]] = self.color
        return f

    # Проверка поля на полностью заполненные линии и их удаление
    def test_line(self):
        global SPEED
        for y in range(self.height):
            f = True
            for i in range(self.width):
                if self.board[y][i] == 0:
                    f = False
                    break
            if f:
                removeLine.play()
                for i in range(y, 0, -1):
                    for j in range(self.width):
                        self.board[i][j] = self.board[i - 1][j]
                self.ingame_counter += 100
                SPEED -= 30 * self.ingame_counter // 200
                pygame.time.set_timer(TIMER, SPEED)
                self.bomb_counter += random.choice([0, 1, 1, 2, 2])

    # Возвращение текущего счёта для отображения на экране
    def score(self):
        return self.ingame_counter

    # Возврат значение True, если игра закончена, иначе False
    def game_over(self):
        return self.end

    # Возвращение текущего количества бомб для отображения на экране
    def num_bomb(self):
        return self.bomb_counter

    # Установка взрыва
    def boom(self):
        if self.bomb_counter > 0:
            explosion.play()
            self.bomb_counter -= 1
            pygame.time.set_timer(TIMER, 0)
            c = 0
            for i in range(len(self.coords)):
                self.board[self.coords[i][0]][self.coords[i][1]] = 0
            while c < 12:
                f = False
                for i in range(18):
                    if self.board[i][c] != 0:
                        self.board[i][c] = 'boom'
                        f = True
                        break
                if not (f):
                    self.board[17][c] = 'boom'
                self.render()
                pygame.display.flip()
                c += 1
            self.delete_bombs()

    # Удаление взрывов с частицами
    def delete_bombs(self):
        c = 0
        while c < 12:
            for i in range(18):
                if self.board[i][c] != 0:
                    create_particles(((c + 0.5) * self.cell_size + self.left,
                                      (i + 0.5) * self.cell_size + self.top))
                    self.board[i][c] = 0
                    break
            self.render()
            pygame.display.flip()
            c += 1
        self.add_to_board()
        pygame.time.set_timer(TIMER, SPEED)


# Частицы взрыва(искры)
class Particle(pygame.sprite.Sprite):
    fire_img = load_image("flare.png")
    fire = []
    fire.append(pygame.transform.scale(fire_img, (40, 40)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()


# Выход из приложения
def terminate():
    pygame.quit()
    sys.exit()


# Начальный экран
def start_screen():
    intro_text = ["PyBoomTetris", "",
                  "Добро пожаловать в тетрис!",
                  "Я думаю, вы знакомы с правилами, это будет взрывное веселье!",
                  "Ах да, взрывное... В этом тетрисе есть 1 отличие от обычного.",
                  "Не все любят ошибаться, и этот тетрис немного исправит ситуацию!",
                  "При активации взрыва каждый верхний блок в каждом столбике",
                  "будет песпощадно взорван!",
                  "Ну что ж, вроде должно быть понятно. Удачи!",
                  "", "",
                  "Управление:",
                  "W - повернуть фигуру, S - установить фигуру,",
                  "A и D - перемещение фигуры по полю,",
                  "R - перезапуск игры, B - бомба.",
                  "", "",
                  "Кнопки в игре:",
                  "'Меню' - вернуться в меню,",
                  "'Пауза' - поставить игру на паузу,",
                  "'Счёт' - показывает текущий счёт(нажать нельзя),",
                  "'Заново' - перезапуск игры(Аналог кнопке R),",
                  "'У вас N бомб' - показывает кол-во зарядов,",
                  "'Выход' - пустите меня отсюда тут сложно.",
                  "", "",
                  "Нажмите в любом месте или любую клавишу для старта."]

    fon = pygame.transform.scale(load_image('title.png'), (850, 950))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 29)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('orange'))
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
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.music.stop()
                new_game()
                return  # начинаем игру
        pygame.display.flip()


# Экран конца игры
def game_over_func():
    gameover.play()
    image = load_image('gameover.png')
    screen.fill((100, 100, 100))
    pygame.mixer.music.stop()

    while True:
        for event in pygame.event.get():
            # выход из программы
            if event.type == pygame.QUIT:
                terminate()

            screen.blit(image, (-1, -1))
            font = pygame.font.Font(None, 25)
            text = font.render('Нажмите R для возврата в меню или закройте приложение для выхода',
                               True, pygame.Color('red'))
            text_rect = text.get_rect()
            text_rect.center = (430, 700)
            screen.blit(text, text_rect)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    start_screen()
                    return
        pygame.display.flip()


# Фон приложения
fon = pygame.transform.scale(load_image('title.png'), (850, 950))


# Функция начала новой игры(Обновляет все значения)
def new_game():
    global running, moving, fig, board, user
    screen.blit(fon, (0, 0))
    board = Board(12, 18)
    running = True
    user = True
    moving = False
    fig = board.figure()
    pygame.time.set_timer(TIMER, SPEED)
    volume = 0.3
    pygame.mixer.music.load('music\OST.mp3')
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)


# Создание частиц
def create_particles(position):
    particle_count = 20
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


# Создание списка спрайтов и таймера для частиц
all_sprites = pygame.sprite.Group()
clock = pygame.time.Clock()

pygame.init()
start_screen()
user = True
new_game()
while running and user:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Обработка нажатий кнопок для игры
        if event.type == pygame.KEYDOWN and not (pause):
            if event.key == pygame.K_b:
                board.boom()
            if event.key == pygame.K_r:
                new_game()
            if event.key == pygame.K_w:
                board.turn_right()
            if event.key == pygame.K_s:
                pygame.time.set_timer(TIMER, 50)
            if event.key == pygame.K_a:
                board.move_left()
            if event.key == pygame.K_d:
                board.move_right()

        # Обработка нажатий кнопок на экране
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 50 <= x <= 150 and 50 <= y <= 150:
                start_screen()
            if 50 <= x <= 150 and 200 <= y <= 350:
                if pause:
                    pygame.time.set_timer(TIMER, SPEED)
                    pause, pause_color = False, 'orange'
                else:
                    pygame.time.set_timer(TIMER, 0)
                    pause, pause_color = True, 'red'
            if 50 <= x <= 150 and 800 <= y <= 900:
                terminate()
            if 50 <= x <= 150 and 500 <= y <= 600:
                new_game()

        if event.type == pygame.KEYUP and not (pause):
            if event.key == pygame.K_s:
                pygame.time.set_timer(TIMER, SPEED)

        if event.type == TIMER and not (pause):
            board.move_down()

    # Проверка того, остановилась ли фигура. Если да, то удалить полные линии и создать новую
    if board.is_stop():
        figPlace.play()
        board.test_line()
        fig = board.figure()

    # Если игра закончилась, то отобразить экран конца игры
    if board.game_over():
        user = False
        record = board.score()
        game_over_func()

    # Фон и весь текст с кнопками на экране
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 25)
    text1 = font.render('Меню', True, pygame.Color('orange'))
    text_rect1 = text1.get_rect()
    text_rect1.center = (100, 100)
    screen.blit(text1, text_rect1)
    text2 = font.render('Пауза', True, pygame.Color(pause_color))
    text_rect2 = text2.get_rect()
    text_rect2.center = (100, 250)
    screen.blit(text2, text_rect2)
    text3 = font.render('Счёт: {}'.format(board.score()), True, pygame.Color('purple'))
    text_rect3 = text3.get_rect()
    text_rect3.center = (100, 380)
    screen.blit(text3, text_rect3)
    text4 = font.render('Заново', True, pygame.Color('yellow'))
    text_rect4 = text4.get_rect()
    text_rect4.center = (100, 550)
    screen.blit(text4, text_rect4)
    text5 = font.render('Выход', True, pygame.Color('red'))
    text_rect5 = text5.get_rect()
    text_rect5.center = (100, 850)
    screen.blit(text5, text_rect5)
    text6 = font.render('У вас есть {} бомб'.format(board.num_bomb()), True, pygame.Color('gold'))
    text_rect6 = text6.get_rect()
    text_rect6.center = (100, 700)
    screen.blit(text6, text_rect6)
    text7 = font.render('Рекорд: {}'.format(str(record)), True, pygame.Color('gold'))
    text_rect7 = text7.get_rect()
    text_rect7.center = (100, 420)
    screen.blit(text7, text_rect7)
    pygame.draw.rect(screen, pygame.Color('green'), (50, 50, 100, 100), 2)
    pygame.draw.rect(screen, pygame.Color('green'), (50, 200, 100, 100), 2)
    pygame.draw.rect(screen, pygame.Color('purple'), (30, 350, 140, 100), 2)
    pygame.draw.rect(screen, pygame.Color('brown'), (50, 500, 100, 100), 5)
    pygame.draw.rect(screen, pygame.Color('red'), (50, 800, 100, 100), 5)
    pygame.draw.rect(screen, pygame.Color('gold'), (20, 650, 160, 100), 5)
    all_sprites.update()
    board.render()
    all_sprites.draw(screen)
    clock.tick(50)
    pygame.display.flip()

if not (running):
    terminate()
