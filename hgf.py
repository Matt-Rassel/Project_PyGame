import pygame
import os
import sys
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TARGET_HEIGHT = 100
TARGET_SIZE = 30  # Размер спрайта
BULLET_SPEED = 10
NUM_TARGETS = 10
TARGET_SPAWN_DELAY = 3200
PLAYER_SPEED = 5
TARGET_SPACING = 500
TARGET_SPEED = 3
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)


def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Target(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = load_image("ship.png")  # Или создайте прямоугольник, как в предыдущем примере
        self.rect = self.image.get_rect(topleft=(x, 100))
        self.speed = 3  # Скорость движения
        self.direction = -1  # 1 - вправо, -1 - влево

    def update(self):
        self.rect.x += self.speed * self.direction


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((5, 10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, WHITE, (0, 0, 5, 10))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED
        dx = target_x - x
        dy = target_y - y
        self.angle = math.atan2(dy, dx)
        self.vx = self.speed * math.cos(self.angle)
        self.vy = self.speed * math.sin(self.angle)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("player.png")  # Замените на имя вашего файла
        self.rect = self.image.get_rect(bottomleft=(50, 300))
        self.speed = PLAYER_SPEED

    def update(self):  # Убрали аргумент keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Shooting Range")
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    targets = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    score = 0
    game_over = False
    last_target_spawn = pygame.time.get_ticks()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Используем координаты центра игрока в качестве цели
                bullet = Bullet(player.rect.centerx, SCREEN_HEIGHT, player.rect.centerx, player.rect.centery)
                all_sprites.add(bullet)
                bullets.add(bullet)
        all_sprites.update()
        now = pygame.time.get_ticks()
        if now - last_target_spawn > TARGET_SPAWN_DELAY:
            x = SCREEN_WIDTH + TARGET_SIZE
            target = Target(x)
            all_sprites.add(target)
            targets.add(target)
            last_target_spawn = now
        if score == NUM_TARGETS:
            game_over = True
        for bullet in bullets:
            collisions = pygame.sprite.spritecollide(bullet, targets, True)
            if collisions:
                bullet.kill()
                score += len(collisions)
        screen.fill(BLACK)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
