import pygame
import os
import sys
import math
import sqlite3
import pygame_gui
import random

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 530
TARGET_HEIGHT = 100
TARGET_SIZE = 30  # Размер спрайта
BULLET_SPEED = 5
NUM_TARGETS = 100
TARGET_SPAWN_DELAY = 3200
PLAYER_SPEED = 5
TARGET_SPACING = 500
TARGET_SPEED = 3
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
H = 500
DATABASE_NAME_uh = 'scores_uh.db'
# --- Цвета ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Загрузка изображений (убедитесь, что файлы существуют в той же директории)
player_image = pygame.image.load("submarine2.png").convert_alpha()
obstacle_image = pygame.image.load("tar.png").convert_alpha()
background_image = pygame.image.load("background1.png").convert()

# База данных
DATABASE_NAME = 'scores.db'


# --- Класс для кнопки меню ---
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height


# --- Класс для меню ---
class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.buttons = [
            Button("Мини-игра 1", 250, 200, 300, 50, (0, 100, 0), (0, 150, 0), self.run_game1),
            Button("Мини-игра 2", 250, 300, 300, 50, (0, 100, 0), (0, 150, 0), self.run_game2),
            Button("Выход", 250, 400, 300, 50, (100, 0, 0), (150, 0, 0), exit),
        ]

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if button.is_clicked(event.pos):
                            button.action()  # Вызывает метод run_game1 или run_game2

            self.draw()  # Отрисовка меню
            pygame.display.flip()
            pygame.time.Clock().tick(60)

        return False  # Вернет False, когда меню закрыто

    def draw(self):
        self.screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            if button.is_clicked(mouse_pos):
                button.color = button.hover_color
            else:
                button.color = (0, 100, 0) if button.action != exit else (100, 0, 0)
            button.draw(self.screen)

    def run_game1(self):
        game1 = Game1(self.screen)
        game1.run()

    def run_game2(self):
        game2 = Game2(self.screen)
        game2.run()


def init_database():
    conn = sqlite3.connect(DATABASE_NAME_uh)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores_uh (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def save_score_uh(score):
    conn = sqlite3.connect(DATABASE_NAME_uh)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores_uh (score) VALUES (?)", (score,))
    conn.commit()
    conn.close()


def get_high_score_uh():
    conn = sqlite3.connect(DATABASE_NAME_uh)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(score) FROM scores_uh")
    high_score = cursor.fetchone()
    conn.close()
    return high_score[0] if high_score else 0


def load_image(name, colorkey=None):
    fullname = os.path.join(name)  # Замените на путь к вашей картинке
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print(f"Cannot load image: {fullname}")
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class Target(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = load_image("ship.png")  # Или создайте прямоугольник, как в предыдущем примере
        self.rect = self.image.get_rect(topleft=(x, 0.05))
        self.speed = 3  # Скорость движения
        self.direction = -1  # 1 - вправо, -1 - влево
        self.image.set_colorkey((255, 255, 255))

    def update(self):
        self.rect.x += self.speed * self.direction


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((5, 10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, WHITE, (0, 0, 5, 10))

        self.speed = BULLET_SPEED  # Assign speed BEFORE using it

        self.rect = self.image.get_rect(center=(x, SCREEN_HEIGHT - self.image.get_height()))

        dx = target_x - x
        dy = target_y - y
        self.angle = math.atan2(dy, dx)

        self.vx = self.speed * math.cos(self.angle)
        self.vy = self.speed * math.sin(self.angle)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.bottom > 530 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.kill()


class Player_uh(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("player1.png")  # Замените на имя вашего файла
        self.rect = self.image.get_rect(bottomleft=(50, 250))
        self.speed = PLAYER_SPEED
        self.image.set_colorkey((0, 0, 0))

    def update(self):  # Убрали аргумент keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed


# --- Класс для мини-игры 1 ---
class Game1:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.background_image = load_image("sea2.png")
        self.boom_image = load_image("boom.png")

        self.all_sprites = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.player = Player_uh()
        self.all_sprites.add(self.player)

        self.score = 0
        self.game_over = False
        self.last_target_spawn = pygame.time.get_ticks()

    def reset(self):
        self.all_sprites.empty()
        self.image = self.boom_image
        self.bullets.empty()
        self.all_sprites.add(self.player)  # Add the player back
        self.score = 0
        self.game_over = False
        self.last_target_spawn = pygame.time.get_ticks()

    def run(self):
        self.reset()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_score_uh(self.score)  # Save the score when game is over
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.game_over:
                    bullet = Bullet(self.player.rect.centerx, SCREEN_HEIGHT, self.player.rect.centerx,
                                    self.player.rect.centery)
                    self.all_sprites.add(bullet)
                    self.bullets.add(bullet)

            self.all_sprites.update()

            # Spawn targets
            now = pygame.time.get_ticks()
            if now - self.last_target_spawn > TARGET_SPAWN_DELAY and not self.game_over:
                x = SCREEN_WIDTH + TARGET_SIZE
                target = Target(x)
                self.all_sprites.add(target)
                self.targets.add(target)
                self.last_target_spawn = now

            # Check for collisions
            for bullet in list(self.bullets):  # Итерируемся по *копии*
                collisions = pygame.sprite.spritecollide(bullet, self.targets, True)
                if collisions:
                    for target in collisions:  # Итерируемся по пораженным целям
                        explosion_rect = self.boom_image.get_rect(center=target.rect.center)
                        self.screen.blit(self.boom_image, explosion_rect)  # Рисуем взрыв
                        pygame.display.flip()  # Немедленно обновляем дисплей
                        pygame.time.delay(200)  # Небольшая задержка для видимости

                    bullet.kill()
                    self.score += len(collisions)

            if self.score >= NUM_TARGETS:  # Check if enough targets hit to win.
                self.game_over = True

            # Drawing
            self.screen.blit(self.background_image, (0, 0))
            self.all_sprites.draw(self.screen)

            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))

            if self.game_over:
                game_over_text = font.render("You Won!", True, WHITE)
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(game_over_text, text_rect)
                # save_score_uh(self.score)  # Save the score when game is over

            pygame.display.flip()
            self.clock.tick(60)
        return


def init_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def save_score(score):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (score) VALUES (?)", (score,))
    conn.commit()
    conn.close()


def get_high_score():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(score) FROM scores")
    high_score = cursor.fetchone()
    conn.close()
    return high_score[0] if high_score else 0


# Классы
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 750))
        self.speed = 4
        self.image.set_colorkey((255, 255, 255))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, speed):
        super().__init__()
        self.image = obstacle_image
        self.rect = self.image.get_rect(x=x, y=0)
        self.speed = speed
        self.image.set_colorkey((255, 255, 255))

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Game2:
    def __init__(self, screen):
        self.screen = screen
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.clock = pygame.time.Clock()
        self.score = 0
        self.game_over = False
        self.last_obstacle_spawn = pygame.time.get_ticks()
        self.obstacle_spawn_delay = 750
        self.obstacle_min_spacing = 50
        self.obstacle_speed = 4
        self.text_color = (255, 255, 255)
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)

    def reset(self):
        self.score = 0
        self.game_over = False
        self.obstacles.empty()
        self.player.rect.center = (SCREEN_WIDTH // 2, 750)
        self.last_obstacle_spawn = pygame.time.get_ticks()

    def run(self, is_running=True):
        self.reset()
        running = is_running
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_over:
                            self.reset()
                        else:
                            running = False

            now = pygame.time.get_ticks()
            if not self.game_over:
                self.score += 1
                score_text = self.font.render(f"Счет: {self.score}", True, self.text_color)
                screen.blit(score_text, (10, 10))
                if now - self.last_obstacle_spawn > self.obstacle_spawn_delay:
                    found_place = False
                    while not found_place:
                        x = random.randint(0, SCREEN_WIDTH - obstacle_image.get_width())
                        valid_position = True
                        for obstacle in self.obstacles:
                            if abs(x - obstacle.rect.x) < self.obstacle_min_spacing:
                                valid_position = False
                                break
                        if valid_position:
                            obstacle = Obstacle(x, self.obstacle_speed)
                            obstacle.rect.y = -obstacle_image.get_height()
                            self.all_sprites.add(obstacle)
                            self.obstacles.add(obstacle)
                            self.last_obstacle_spawn = now
                            found_place = True

                self.all_sprites.update()
                for obstacle in list(self.obstacles):
                    if obstacle.rect.top > SCREEN_HEIGHT:
                        self.score += 1
                        obstacle.kill()

                if pygame.sprite.spritecollide(self.player, self.obstacles, True, pygame.sprite.collide_mask):
                    self.game_over = True

            self.screen.blit(background_image, (0, 0))
            self.all_sprites.draw(self.screen)
            score_text = self.font.render(f"Счет: {self.score}", True, self.text_color)
            self.screen.blit(score_text, (10, 10))
            if self.game_over:
                game_over_text = self.game_over_font.render("Игра окончена!", True, self.text_color)
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(game_over_text, text_rect)
                press_space = self.font.render("Нажмите пробел для перезапуска", True, self.text_color)
                press_space_rect = press_space.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                self.screen.blit(press_space, press_space_rect)
                save_score(self.score)  # Сохраняем счет в базу данных

            pygame.display.flip()
            self.clock.tick(60)
        return  # Возврат в меню


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Игра с мини-играми")

    menu = Menu(screen)
    in_menu = True
    while in_menu:
        in_menu = menu.run()  # Цикл меню
    pygame.quit()


if __name__ == "__main__":
    main()
