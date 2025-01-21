import pygame
import os
import sys
import math
import sqlite3
import pygame_gui

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 530
TARGET_HEIGHT = 100
TARGET_SIZE = 30  # Размер спрайта
BULLET_SPEED = 5
NUM_TARGETS = 10
TARGET_SPAWN_DELAY = 3200
PLAYER_SPEED = 5
TARGET_SPACING = 500
TARGET_SPEED = 3
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
H = 500
DATABASE_NAME = 'scores_uh.db'


def init_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores_uh (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def save_score(score):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores_uh (score) VALUES (?)", (score,))
    conn.commit()
    conn.close()


def get_high_score():
    conn = sqlite3.connect(DATABASE_NAME)
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


class Player(pygame.sprite.Sprite):
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


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.background_image = load_image("sea2.png")

        self.all_sprites = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)

        self.score = 0
        self.game_over = False
        self.last_target_spawn = pygame.time.get_ticks()


    def reset(self):
        self.all_sprites.empty()
        self.targets.empty()
        self.bullets.empty()
        self.all_sprites.add(self.player) # Add the player back
        self.score = 0
        self.game_over = False
        self.last_target_spawn = pygame.time.get_ticks()



    def run(self):
        self.reset()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit() # Correctly exit the program
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.game_over:
                    bullet = Bullet(self.player.rect.centerx, SCREEN_HEIGHT, self.player.rect.centerx, self.player.rect.centery)
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
            for bullet in self.bullets:
                collisions = pygame.sprite.spritecollide(bullet, self.targets, True)
                if collisions:
                    bullet.kill()
                    self.score += len(collisions)


            if self.score >= NUM_TARGETS: # Check if enough targets hit to win.
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
                save_score(self.score) # Save the score when game is over



            pygame.display.flip()
            self.clock.tick(70)

class Menu:
    def __init__(self, screen, game):
        self.screen = screen
        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.game = game
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50),
            text='Начать игру',
            manager=self.manager
        )
        self.high_score = get_high_score()
        self.high_score_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 75, 200, 50),
            text=f'Рекорд: {self.high_score}',
            manager=self.manager
        )

    def run(self):
        running = True
        while running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.start_button:
                            running = False
                            self.game.run()
                            self.high_score = get_high_score()
                            self.high_score_label.set_text(f'Рекорд: {self.high_score}')
                            return
                self.manager.process_events(event)

            self.manager.update(time_delta)
            self.screen.fill((0, 0, 0))
            self.manager.draw_ui(self.screen)
            pygame.display.update()


def main():
    init_database()
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = Game(screen)
    menu = Menu(screen, game)
    menu.run()
    pygame.quit()


if __name__ == "__main__":
    main()
