import pygame
import random
WHITE = (255, 255, 255)
pygame.init()
WIDTH, HEIGHT = 1399, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Уворачивайся!")
player_image = pygame.image.load("submarine2.png").convert_alpha()
obstacle_image = pygame.image.load("tar.png").convert_alpha()
background_image = pygame.image.load("background1.png").convert()  # Загружаем фон
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, 750))
        self.speed = 4
        self.image.set_colorkey((255, 255, 255))
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
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
        if self.rect.top > HEIGHT:
            self.kill()
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
clock = pygame.time.Clock()
running = True
score = 0
game_over = False
last_obstacle_spawn = pygame.time.get_ticks()
obstacle_spawn_delay = 750
obstacle_min_spacing = 50
obstacle_speed = 4
text_color = (255, 255, 255)  # белый
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)  # Более крупный шрифт для Game Over
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                game_over = False
                score = 0
                obstacles.empty()
                player.rect.center = (WIDTH // 2, 750)
    now = pygame.time.get_ticks()
    if now - last_obstacle_spawn > obstacle_spawn_delay:
        found_place = False
        while not found_place:
            x = random.randint(0, WIDTH - obstacle_image.get_width())  # Учитываем ширину изображения
            valid_position = True
            for obstacle in obstacles:
                if abs(x - obstacle.rect.x) < obstacle_min_spacing:
                    valid_position = False
                    break
            if valid_position:
                obstacle = Obstacle(x, obstacle_speed)
                obstacle.rect.y = -obstacle_image.get_height()  # Начало за верхней границей
                all_sprites.add(obstacle)
                obstacles.add(obstacle)
                last_obstacle_spawn = now
                found_place = True
    all_sprites.update()
    if pygame.sprite.spritecollide(player, obstacles, True, pygame.sprite.collide_mask):
        game_over = True
    screen.blit(background_image, (0, 0))  # Рисуем фон
    all_sprites.draw(screen)
    if not game_over:
        score += 1
        score_text = font.render(f"Счет: {score}", True, text_color)
        screen.blit(score_text, (10, 10))
    else:
        game_over_text = game_over_font.render("GAME OVER", True, text_color)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(game_over_text, text_rect)
        score_text = font.render(f"Ваш счет: {score}", True, text_color)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(score_text, score_rect)
        instruction_text = font.render("Нажмите ПРОБЕЛ, чтобы начать заново", True, text_color)
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        screen.blit(instruction_text, instruction_rect)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
                                                                                               