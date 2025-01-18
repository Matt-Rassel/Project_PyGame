import random
import pygame
import pygame_gui

# Константы
WHITE = (255, 255, 255)
WIDTH, HEIGHT = 1399, 1000
MAX_OBSTACLES = 10
# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Уворачивайся!")

# Загрузка изображений (убедитесь, что файлы существуют в той же директории)
player_image = pygame.image.load("submarine2.png").convert_alpha()
obstacle_image = pygame.image.load("tar.png").convert_alpha()
background_image = pygame.image.load("background1.png").convert()


# Классы
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


class Game:
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
        self.player.rect.center = (WIDTH // 2, 750)
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
                if len(self.obstacles) < MAX_OBSTACLES:
                    if now - self.last_obstacle_spawn > self.obstacle_spawn_delay:
                        while not found_place:
                            attempts = 0
                            MAX_ATTEMPTS = 100  # Or some other reasonable number

                            x = random.randint(0, WIDTH - obstacle_image.get_width())
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
                            else:
                                attempts += 1
                                if attempts >= MAX_ATTEMPTS:
                                    print("Couldn't find a valid position for the obstacle after multiple attempts.")
                                    break  # Exit the while loop even if no place is found

                            if not found_place and attempts >= MAX_ATTEMPTS:
                                self.obstacle_spawn_delay += 100  # Increase delay if no valid pos is found
                                print(f"Increased spawn delay to {self.obstacle_spawn_delay}ms.")
                        if not found_place:
                            continue
                self.all_sprites.update()
                for obstacle in list(self.obstacles):
                    if obstacle.rect.top > HEIGHT:
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
                text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(game_over_text, text_rect)
                press_space = self.font.render("Нажмите пробел для перезапуска", True, self.text_color)
                press_space_rect = press_space.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
                self.screen.blit(press_space, press_space_rect)

            pygame.display.flip()
            self.clock.tick(60)


class Menu:
    def __init__(self, screen, game):
        self.screen = screen
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.game = game
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50),
            text='Начать игру',
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
                            return
                self.manager.process_events(event)

            self.manager.update(time_delta)
            self.screen.fill((0, 0, 0))
            self.manager.draw_ui(self.screen)
            pygame.display.update()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    game = Game(screen)
    menu = Menu(screen, game)
    menu.run()
    pygame.quit()


if __name__ == "__main__":
    main()
