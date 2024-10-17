import pygame
import time

class Renderer:
    def __init__(self, logic):
        self.logic = logic
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Snake Game')
        self.splash_image = self.load_image('snake.png')
        self.start_image = self.load_image('bg.png')
        self.background = self.load_image('game_bg.png')

    def load_image(self, filename):
        try:
            image = pygame.image.load(filename)
            return pygame.transform.scale(image, (640, 480))
        except pygame.error as e:
            print(f"Error loading image {filename}: {e}")
            return None

    def show_splash_screen(self):
        if self.splash_image:
            self.screen.blit(self.splash_image, (0, 0))
            pygame.display.update()
            pygame.event.pump()
            time.sleep(2)

    def show_start_screen(self):
        if self.start_image:
            self.screen.blit(self.start_image, (0, 0))
            self.draw_text('Press SPACE to start or ESC to quit', 25, (0, 255, 0), 320, 380)
            pygame.display.flip()
            self.wait_for_key([pygame.K_SPACE, pygame.K_ESCAPE])

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.SysFont('arial', size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def wait_for_key(self, keys):
        waiting = True
        while waiting and self.logic.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.logic.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key in keys:
                        if event.key == pygame.K_SPACE:
                            waiting = False
                        elif event.key == pygame.K_ESCAPE:
                            self.logic.running = False
                            waiting = False

    def render(self):
        self.screen.fill((0, 0, 0))
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        for part in self.logic.snake_body:
            pygame.draw.rect(self.screen, (0, 255, 0), (part[0], part[1], 10, 10))
        pygame.draw.rect(self.screen, (255, 0, 0), (self.logic.food_pos[0], self.logic.food_pos[1], 10, 10))

        self.draw_text(str(self.logic.score), 25, (0, 0, 0), 320, 5)
        pygame.draw.rect(self.screen, (255, 255, 255), (70, 70, 500, 340), 1)
        pygame.display.update()

    def show_game_over_screen(self):
        self.screen.fill((0, 0, 0))
        self.draw_text('Game Over', 50, (255, 0, 0), 320, 200)
        self.draw_text('Press ESC to quit', 25, (255, 255, 255), 320, 260)
        pygame.display.flip()
        self.wait_for_key([pygame.K_ESCAPE])
