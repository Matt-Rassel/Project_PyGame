import pygame
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TARGET_HEIGHT = 200
TARGET_SIZE = 30
TARGET_SPEED = 3
BULLET_SPEED = 10
NUM_TARGETS = 10
TARGET_SPAWN_DELAY = 1000  # in milliseconds
PLAYER_SPEED = 5
TARGET_SPACING = 20  # Spacing between targets
PLAYER_HEIGHT = TARGET_HEIGHT + TARGET_SIZE // 2  # player height aligned with targets

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)


class Target:
    def __init__(self, x):
        self.x = x
        self.y = TARGET_HEIGHT
        self.width = TARGET_SIZE
        self.height = TARGET_SIZE
        self.speed = TARGET_SPEED

    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            return False  # Target is offscreen
        return True  # Target is still onscreen

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

    def is_hit(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = BULLET_SPEED

    def update(self):
        self.y -= self.speed  # Now moves upwards
        if self.y < 0:
            return False  # Bullet is offscreen
        return True

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 3)


class Player:
    def __init__(self):
        self.x = 50
        self.y = PLAYER_HEIGHT  # Aligned with targets
        self.width = 20
        self.height = 20
        self.speed = PLAYER_SPEED

    def update(self, keys):
        if keys[pygame.K_a] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Shooting Range")
    clock = pygame.time.Clock()

    targets = []
    bullets = []
    player = Player()
    score = 0
    game_over = False
    last_target_spawn = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullet_x = player.x + player.width // 2  # Center horizontally
                bullets.append(Bullet(bullet_x, SCREEN_HEIGHT - 10))  # Shoot from bottom

        keys = pygame.key.get_pressed()
        player.update(keys)

        # Update bullets
        for bullet in bullets[:]:
            if not bullet.update():
                bullets.remove(bullet)
            for target in targets[:]:
                if target.is_hit(bullet.x, bullet.y):
                    targets.remove(target)
                    score += 1
                    bullets.remove(bullet)
                    break

        for target in targets[:]:
            if not target.update():
                targets.remove(target)

        # Spawn targets
        now = pygame.time.get_ticks()
        if now - last_target_spawn > TARGET_SPAWN_DELAY and len(targets) < NUM_TARGETS:
            last_x = 0
            if targets:
                last_x = targets[-1].x
            targets.append(Target(SCREEN_WIDTH + last_x + TARGET_SPACING))
            last_target_spawn = now

        # Check if won
        if score == NUM_TARGETS:
            game_over = True

        screen.fill(BLACK)
        player.draw(screen)
        for target in targets:
            target.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)

        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))

        if game_over:
            game_over_text = font.render("You Won!", True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(game_over_text, text_rect)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()


if __name__ == "__main__":
    main()
