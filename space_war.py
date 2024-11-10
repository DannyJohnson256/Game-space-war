import pygame
import random
from os import path

# указание папки, в которой находятся все файлы графики и музыки
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

# размеры окна
WIDTH = 520
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000

# цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (128, 128, 128)
INV = (71, 112, 77)

# окно игры
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space war")
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial') # шрифт игры

# отображение счёта
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# полоска, отображающая здоровье
def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

# отображение количества жизней
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

# экран окончания игры (появляется при запуске)
def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "Shooter in space", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, '''Клавиши со стрелками для перемещения''', 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, '''Пробел для стрельбы''', 22, WIDTH / 2, HEIGHT * 55 / 100)
    draw_text(screen, "Нажмите клавишу, чтобы начать", 18, WIDTH / 2, HEIGHT * 4 / 5)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

# игрок
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        # прозрачный фон убрать надо
        self.image.set_colorkey()
        self.rect = self.image.get_rect()
        self.radius = 20 # указание радиуса столкновения
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100 # количество здоровья
        self.shoot_delay = 250 # время между выстрелами (авто-огонь)
        self.last_shot = pygame.time.get_ticks() # авто-огонь
        self.lives = 3 # количество жизней
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    # обновление игрока
    def update(self):
        # время для улучшений
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()
            
        # скрыть игрока, если он умер
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        
        # передвижение игрока
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        
        # авто-огонь
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
