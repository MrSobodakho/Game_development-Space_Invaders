import pygame
import sys
from Gun import Gun

def run(): #создание объекта экрана (создание размера отображаемой области, заголовка, цвет фона)
    pygame.init() #инициализация игры
    screen = pygame.display.set_mode((400, 500))
    pygame.display.set_caption("Space Invaders")
    bg_color = (0, 0, 0)
    gun = Gun(screen) #Создаём объект корабля

    while True: #Обработка всех событий пользователя в игре
        for event in pygame.event.get():
           if event.type == pygame.QUIT: # Обработка события, когда пользователь хочет выйти из игры
               sys.exit()

        screen.fill(bg_color)
        gun.output()
        pygame.display.flip() # Прорисовка последнего экрана
run()