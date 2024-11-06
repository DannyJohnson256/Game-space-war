import pygame
import random
from os import path

# указание папки, в которой находятся все файлы графики и музыки
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

# размеры окна
WIDTH = 520
HEIGHT = 600

# цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (128, 128, 128)
INV = (71, 112, 77)
