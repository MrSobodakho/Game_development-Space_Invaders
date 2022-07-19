import pygame
import random
import math
from pygame import mixer
import time

# игровые константы
WIDTH = 800
HEIGHT = 600

# глобальные переменные с начальными значениями
running = True
pause_state = 0
score = 0
highest_score = 0
life = 2
kills = 0
difficulty = 1
level = 1
max_kills_to_difficulty_up = 3
max_difficulty_to_level_up = 2
initial_player_velocity = 3.0
initial_enemy_velocity = 0.2
weapon_shot_velocity = 4.0
single_frame_rendering_time = 0
total_time = 0
frame_count = 0
fps = 0

# создание объектов
player = type('Player', (), {})()
bullet = type('Bullet', (), {})()
enemies = []
lasers = []

# инициализация объектов pygame
pygame.init()

# создание состояния клавиш ввода
LEFT_ARROW_KEY_PRESSED = 0
RIGHT_ARROW_KEY_PRESSED = 0
SPACE_BAR_PRESSED = 0
ESC_KEY_PRESSED = 0

# создание окна отображения
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
window_icon = pygame.image.load("images/alien.png")
pygame.display.set_icon(window_icon)

# создание переменных (игровая музыка)
pause_sound = None
level_up_sound = None
weapon_annihilation_sound = None
game_over_sound = None

# создание фона
background_img = pygame.image.load("images/background.jpg")  # 800 x 600 px image
background_music_paths = ["sounds/background music.ogg",
                          "sounds/background music_x2.ogg",
                          "sounds/background music_x4.ogg",
                          "sounds/background music_x8.ogg",
                          "sounds/background music_x16.ogg",
                          "sounds/background music_x32.ogg"]


def init_background_music(): #инициализация фоновой музыки
    if difficulty == 1:
        mixer.quit()
        mixer.init()
    if difficulty <= 6:
        mixer.music.load(background_music_paths[difficulty - 1])
    else:
        mixer.music.load(background_music_paths[5])
    mixer.music.play(-1)


# создание класса игрока
class Player:
    def __init__(self, img_path, width, height, x, y, dx, dy, kill_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.kill_sound_path = kill_sound_path
        self.kill_sound = mixer.Sound(self.kill_sound_path)

    def draw(self):
        window.blit(self.img, (self.x, self.y))


# создание класса врага
class Enemy:
    def __init__(self, img_path, width, height, x, y, dx, dy, kill_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.kill_sound_path = kill_sound_path
        self.kill_sound = mixer.Sound(self.kill_sound_path)

    def draw(self): #отрисовка врага
        window.blit(self.img, (self.x, self.y))


# создание выстрела
class Bullet:
    def __init__(self, img_path, width, height, x, y, dx, dy, fire_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.fired = False
        self.fire_sound_path = fire_sound_path
        self.fire_sound = mixer.Sound(self.fire_sound_path)

    def draw(self):
        if self.fired:
            window.blit(self.img, (self.x, self.y))


# создание лазера
class Laser:
    def __init__(self, img_path, width, height, x, y, dx, dy, shoot_probability, relaxation_time, beam_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.beamed = False
        self.shoot_probability = shoot_probability
        self.shoot_timer = 0
        self.relaxation_time = relaxation_time
        self.beam_sound_path = beam_sound_path
        self.beam_sound = mixer.Sound(self.beam_sound_path)

    def draw(self):
        if self.beamed:
            window.blit(self.img, (self.x, self.y))


def scoreboard(): #создание текстового стенда
    x_offset = 10
    y_offset = 10
    # создание стиля и размера шрифта
    font = pygame.font.SysFont("time", 20)

    #параметры текста
    score_sprint = font.render("СЧЕТ : " + str(score), True, (7, 19, 231))
    highest_score_sprint = font.render("ЛУЧШИЙ РЕЗУЛЬТАТ : " + str(highest_score), True, (7, 19, 231))
    level_sprint = font.render("УРОВЕНЬ : " + str(level), True, (7, 19, 231))
    difficulty_sprint = font.render("СЛОЖНОСТЬ : x" + str(difficulty), True, (7, 19, 231))
    life_sprint = font.render("КОЛИЧЕСТВО ЖИЗНЕЙ : " + str(life), True, (7, 19, 231))
    fps_sprint = font.render("FPS : " + str(fps), True, (40, 218, 20))

    # разметка текста в окне
    window.blit(score_sprint, (x_offset, y_offset))
    window.blit(highest_score_sprint, (x_offset, y_offset + 20))
    window.blit(level_sprint, (x_offset, y_offset + 40))
    window.blit(difficulty_sprint, (x_offset, y_offset + 60))
    window.blit(life_sprint, (x_offset, y_offset + 80))
    window.blit(fps_sprint, (WIDTH - 80, y_offset + 20))


def collision_check(object1, object2): #проверка столкновений
    x1_cm = object1.x + object1.width / 2
    y1_cm = object1.y + object1.width / 2
    x2_cm = object2.x + object2.width / 2
    y2_cm = object2.y + object2.width / 2
    distance = math.sqrt(math.pow((x2_cm - x1_cm), 2) + math.pow((y2_cm - y1_cm), 2))
    return distance < ((object1.width + object2.width) / 2)

def level_up(): #обработка уровней
    global life
    global level
    global difficulty
    global max_difficulty_to_level_up
    level_up_sound.play()
    level += 1
    life += 1       #добавление жизни на новом уровне
    difficulty = 1  # сброс сложности на новом уровне

    if level % 3 == 0:
        player.dx += 1
        bullet.dy += 1
        max_difficulty_to_level_up += 1
        for each_laser in lasers:
            each_laser.shoot_probability += 1.0
            if each_laser.shoot_probability > 6.0:
                each_laser.shoot_probability = 1.0
    if max_difficulty_to_level_up > 4:
        max_difficulty_to_level_up = 4

    font = pygame.font.SysFont("time", 50) #создание текста при переходе на новый уровень
    gameover_sprint = font.render("NEXT LEVEL", True, (6, 232, 12))
    window.blit(gameover_sprint, (WIDTH / 2 - 110, HEIGHT / 2 - 32))
    pygame.display.update()
    init_game()
    time.sleep(1.0)


def respawn(enemy_obj): #возрождение врага (с рандомными координатами появления)
    enemy_obj.x = random.randint(0, (WIDTH - enemy_obj.width))
    enemy_obj.y = random.randint(((HEIGHT / 10) * 1 - (enemy_obj.height / 2)),
                                 ((HEIGHT / 10) * 4 - (enemy_obj.height / 2)))


def kill_enemy(player_obj, bullet_obj, enemy_obj):
    global score
    global kills
    global difficulty
    bullet_obj.fired = False
    enemy_obj.kill_sound.play()
    bullet_obj.x = player_obj.x + player_obj.width / 2 - bullet_obj.width / 2
    bullet_obj.y = player_obj.y + bullet_obj.height / 2
    score = score + 10 * difficulty * level
    kills += 1
    if kills % max_kills_to_difficulty_up == 0:
        difficulty += 1
        if (difficulty == max_difficulty_to_level_up) and (life != 0):
            level_up()
        init_background_music()
    respawn(enemy_obj)


def rebirth(player_obj):
    player_obj.x = (WIDTH / 2) - (player_obj.width / 2)
    player_obj.y = (HEIGHT / 10) * 9 - (player_obj.height / 2)


def gameover_screen(): #текст при завершении игры
    scoreboard()
    font = pygame.font.SysFont("time", 70)
    gameover_sprint = font.render("GAME OVER", True, (255, 255, 255))
    window.blit(gameover_sprint, (WIDTH / 2 - 140, HEIGHT / 2 - 32))
    pygame.display.update()

    mixer.music.stop()
    game_over_sound.play()
    time.sleep(13.0)
    mixer.quit()


def gameover():
    global running
    global score
    global highest_score

    if score > highest_score:
        highest_score = score

    running = False
    gameover_screen()

#действия при убийстве игрока
def kill_player(player_obj, enemy_obj, laser_obj):
    global life
    laser_obj.beamed = False
    player_obj.kill_sound.play()
    laser_obj.x = enemy_obj.x + enemy_obj.width / 2 - laser_obj.width / 2
    laser_obj.y = enemy_obj.y + laser_obj.height / 2
    life -= 1
    if life > 0:
        rebirth(player_obj)
    else:
        gameover()

# действия при столкновении пуль
def destroy_weapons(player_obj, bullet_obj, enemy_obj, laser_obj):
    bullet_obj.fired = False
    laser_obj.beamed = False
    weapon_annihilation_sound.play()
    bullet_obj.x = player_obj.x + player_obj.width / 2 - bullet_obj.width / 2
    bullet_obj.y = player_obj.y + bullet_obj.height / 2
    laser_obj.x = enemy_obj.x + enemy_obj.width / 2 - laser_obj.width / 2
    laser_obj.y = enemy_obj.y + laser_obj.height / 2

#режим паузы в игре
def pause_game():
    pause_sound.play()
    scoreboard()
    font = pygame.font.SysFont("time", 70)
    gameover_sprint = font.render("ПАУЗА", True, (255, 255, 255))
    window.blit(gameover_sprint, (WIDTH / 2 - 80, HEIGHT / 2 - 32))
    pygame.display.update()
    mixer.music.pause()


def init_game(): #инициализация игровых объектов и звуков
    global pause_sound
    global level_up_sound
    global game_over_sound
    global weapon_annihilation_sound

    pause_sound = mixer.Sound("sounds/pause.wav")
    level_up_sound = mixer.Sound("sounds/next_level.wav")
    game_over_sound = mixer.Sound("sounds/game_over.wav")
    weapon_annihilation_sound = mixer.Sound("sounds/annihilation.wav")

    # игрок
    player_img_path = "images/spaceship.png"
    player_width = 87
    player_height = 64
    player_x = (WIDTH / 2) - (player_width / 2)
    player_y = (HEIGHT / 10) * 9 - (player_height / 2)
    player_dx = initial_player_velocity
    player_dy = 0
    player_kill_sound_path = "sounds/explosion.wav"

    global player
    player = Player(player_img_path, player_width, player_height, player_x, player_y, player_dx, player_dy,
                    player_kill_sound_path)

    # пуля
    bullet_img_path = "images/bullet.png"
    bullet_width = 32
    bullet_height = 32
    bullet_x = player_x + player_width / 2 - bullet_width / 2
    bullet_y = player_y + bullet_height / 2
    bullet_dx = 0
    bullet_dy = weapon_shot_velocity
    bullet_fire_sound_path = "sounds/gunshot.wav"

    global bullet
    bullet = Bullet(bullet_img_path, bullet_width, bullet_height, bullet_x, bullet_y, bullet_dx, bullet_dy,
                    bullet_fire_sound_path)

    # враг
    enemy_img_path = "images/enemy.png"
    enemy_width = 64
    enemy_height = 64
    enemy_dx = initial_enemy_velocity
    enemy_dy = (HEIGHT / 10) / 2
    enemy_kill_sound_path = "sounds/enemykill.wav"

    # луч врага
    laser_img_path = "images/beam.png"
    laser_width = 24
    laser_height = 24
    laser_dx = 0
    laser_dy = weapon_shot_velocity
    shoot_probability = 0.05
    relaxation_time = 100
    laser_beam_sound_path = "sounds/laser.wav"

    global enemies
    global lasers

    enemies.clear()
    lasers.clear()

    for lev in range(level):
        enemy_x = random.randint(0, (WIDTH - enemy_width))
        enemy_y = random.randint(((HEIGHT / 10) * 1 - (enemy_height / 2)), ((HEIGHT / 10) * 4 - (enemy_height / 2)))
        laser_x = enemy_x + enemy_width / 2 - laser_width / 2
        laser_y = enemy_y + laser_height / 2

        enemy_obj = Enemy(enemy_img_path, enemy_width, enemy_height, enemy_x, enemy_y, enemy_dx, enemy_dy,
                          enemy_kill_sound_path)
        enemies.append(enemy_obj)

        laser_obj = Laser(laser_img_path, laser_width, laser_height, laser_x, laser_y, laser_dx, laser_dy,
                          shoot_probability, relaxation_time, laser_beam_sound_path)
        lasers.append(laser_obj)


# начало игры
init_game()
init_background_music()
runned_once = False

# основной игровой цикл
while running:
    start_time = time.time()

    # прорисовка действий в игре
    window.fill((0, 0, 0))
    window.blit(background_img, (0, 0))

    # регистрация событий
    for event in pygame.event.get():
        # завершение события (крестик)
        if event.type == pygame.QUIT:
            running = False

        # события при нажатии клавиш
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                LEFT_ARROW_KEY_PRESSED = 1
            if event.key == pygame.K_RIGHT:
                RIGHT_ARROW_KEY_PRESSED = 1
            if event.key == pygame.K_SPACE:
                SPACE_BAR_PRESSED = 1
            if event.key == pygame.K_ESCAPE:
                ESC_KEY_PRESSED = 1
                pause_state += 1

        # события при отпускании клавиш
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                RIGHT_ARROW_KEY_PRESSED = 0
            if event.key == pygame.K_LEFT:
                LEFT_ARROW_KEY_PRESSED = 0
            if event.key == pygame.K_SPACE:
                SPACE_BAR_PRESSED = 0
            if event.key == pygame.K_ESCAPE:
                print("LOG: Escape Key Released")
                ESC_KEY_PRESSED = 0

    # проверка событий паузы в игре
    if pause_state == 2:
        pause_state = 0
        runned_once = False
        mixer.music.unpause()
    if pause_state == 1:
        if not runned_once:
            runned_once = True
            pause_game()
        continue

    if RIGHT_ARROW_KEY_PRESSED:
        player.x += player.dx
    if LEFT_ARROW_KEY_PRESSED:
        player.x -= player.dx
    # bullet firing
    if (SPACE_BAR_PRESSED) and not bullet.fired:
        bullet.fired = True
        bullet.fire_sound.play()
        bullet.x = player.x + 25 #координаты старта выстрела
        bullet.y = player.y + 5

    # создание движения пули
    if bullet.fired:
        bullet.y -= bullet.dy

    # создание прозрачности лазеров врагов через самих себя
    for i in range(len(enemies)):
        if not lasers[i].beamed:
            lasers[i].shoot_timer += 1
            if lasers[i].shoot_timer == lasers[i].relaxation_time:
                lasers[i].shoot_timer = 0
                random_chance = random.randint(0, 100)
                if random_chance <= (lasers[i].shoot_probability * 100):
                    lasers[i].beamed = True
                    lasers[i].beam_sound.play()
                    lasers[i].x = enemies[i].x + enemies[i].width / 2 - lasers[i].width / 2
                    lasers[i].y = enemies[i].y + lasers[i].height / 2
        # движение врага
        enemies[i].x += enemies[i].dx * float(2 ** (difficulty - 1))
        # движение лазера
        if lasers[i].beamed:
            lasers[i].y += lasers[i].dy

    # проверка на столкновение
    for i in range(len(enemies)):
        bullet_enemy_collision = collision_check(bullet, enemies[i])
        if bullet_enemy_collision:
            kill_enemy(player, bullet, enemies[i])

    for i in range(len(lasers)):
        laser_player_collision = collision_check(lasers[i], player)
        if laser_player_collision:
            kill_player(player, enemies[i], lasers[i])

    for i in range(len(enemies)):
        enemy_player_collision = collision_check(enemies[i], player)
        if enemy_player_collision:
            kill_enemy(player, bullet, enemies[i])
            kill_player(player, enemies[i], lasers[i])

    for i in range(len(lasers)):
        bullet_laser_collision = collision_check(bullet, lasers[i])
        if bullet_laser_collision:
            destroy_weapons(player, bullet, enemies[i], lasers[i])

    # проверка границ
    # у игрока
    if player.x < 0:
        player.x = 0
    if player.x > WIDTH - player.width:
        player.x = WIDTH - player.width
    # у врага
    for enemy in enemies:
        if enemy.x <= 0:
            enemy.dx = abs(enemy.dx) * 1
            enemy.y += enemy.dy
        if enemy.x >= WIDTH - enemy.width:
            enemy.dx = abs(enemy.dx) * -1
            enemy.y += enemy.dy
    # у пули
    if bullet.y < 0:
        bullet.fired = False
        bullet.x = player.x + player.width / 2 - bullet.width / 2
        bullet.y = player.y + bullet.height / 2
    # у лазера
    for i in range(len(lasers)):
        if lasers[i].y > HEIGHT:
            lasers[i].beamed = False
            lasers[i].x = enemies[i].x + enemies[i].width / 2 - lasers[i].width / 2
            lasers[i].y = enemies[i].y + lasers[i].height / 2

    # создание рамки, с размещением объектов на поверхности
    scoreboard()
    for laser in lasers:
        laser.draw()
    for enemy in enemies:
        enemy.draw()
    bullet.draw()
    player.draw()

    # визуализация экрана
    pygame.display.update()

    # определение FPS
    frame_count += 1
    end_time = time.time()
    single_frame_rendering_time = end_time - start_time
    total_time = total_time + single_frame_rendering_time
    if total_time >= 1.0:
        fps = frame_count
        frame_count = 0
        total_time = 0