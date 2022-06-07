import pygame

class Gun():

    def __init__(self, screen):
        '''инициализация корабля'''
        self.screen = screen
        self.image = pygame.image.load("images/spaceship.png") #загрузка изображения в проект
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        self.rect.centerx = self.screen_rect.centerx #координаты корабля по центру графического объекта
        self.rect.bottom = self.screen_rect.bottom #нижние координаты

    def output(self): #отрисовка корабля
        self.screen.blit(self.image, self.rect)