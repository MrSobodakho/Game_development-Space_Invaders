import pygame, controls
from gun import Gun
from pygame.sprite import Group
from stats import Stats
from scores import Scores

WIDTH = 800
HEIGHT = 600
background_img = pygame.image.load("images/background.jpg")

def run(): #Запуск и инициализация экрана
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Invaders")
    window_icon = pygame.image.load("images/alien.png")
    pygame.display.set_icon(window_icon)
#    bg_color = (0, 0, 0)
    gun = Gun(screen)
    bullets = Group()
    inos = Group()
    controls.create_army(screen, inos)
    stats = Stats()
    sc = Scores(screen, stats)

    while True: #обработка всех событий (действия на экране)
        controls.events(screen, gun, bullets)
        if stats.run_game:
            gun.update_gun()
            controls.update(background_img, screen, stats, sc, gun, inos, bullets)
            controls.update_bullets(screen, stats, sc, inos, bullets)
            controls.update_inos(stats, screen, sc, gun, inos, bullets)

run()