import pygame
import random
from os import path

# указание папки, в которой находятся все файлы графики и музыки
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

# размеры окна
WIDTH = 520
HEIGHT = 600

#количество кадров в секунду
FPS = 60

# время действия улучшений
POWERUP_TIME = 5000

#первоначальный счет
score = 0

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

# функция добавления метеорита 
def newmob(): 
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

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
            
    # подбор улучшений
    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    # добавление снарядов (авто-огонь)
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            # стрельба двумя снарядами, если заряд выше 2
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
                
    # временно скрыть игрока       
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200) #####
# метеорит
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        # создание прозрачного фона
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2) # радиус столкновения

        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0 # вращение по градусам
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    # функция вращения
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    #обновление с течением времени
    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

# стрельба
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# улучшения
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        # альфа
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

# взрывы
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# изображения корабля, снарядов и метеоритов
background = pygame.image.load(path.join(img_dir, "звездное небо фона.png")).convert_alpha()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "кораблик.png")).convert_alpha()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, "снаряд.png")).convert_alpha()
meteor_images = []
meteor_list = ['метеор большой.png', 'метеор средний 1.png',
               'метеор средний 2.png', 'метеор маленький 1.png', 'метеор маленький 2.png',
               'метеор мизерный.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert_alpha())

# изображения улучшений
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'щит.png')).convert_alpha()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'энергия.png')).convert_alpha()

# загрузка анимации
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'взрыв{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'звуковая_волна{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

# звуки
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'звук выстрела.wav'))
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'звук подбора хитпоинтов.wav'))
power_sound = pygame.mixer.Sound(path.join(snd_dir, 'звук подбора улучшения для доп мощи.wav'))
expl_sounds = []
for snd in ['звук взрыва метеорита 1.wav', 'звук взрыва метеорита 2.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
pygame.mixer.music.load(path.join(snd_dir, 'music in game.ogg'))
pygame.mixer.music.set_volume(0.4)

# спрайты
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
# настройка максимального количества метеоритов на экране
for i in range(8):
    newmob()
pygame.mixer.music.play(loops=-1) # подключение музыки
