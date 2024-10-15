import pygame
import random
import socket
import threading
import json
import time

class SnakeGame:
    # Game Constants
    WIDTH, HEIGHT = 640, 480
    BORDER_OFFSET = 70
    SNAKE_SIZE = 10
    FPS = 15

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    def __init__(self):
        # Socket setup
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(1.0)
        try:
            self.client.connect(('0.0.0.0', 5555))  # Listen on all network interfaces
        except socket.error:
            print("Unable to connect to the server.")
            self.running = False
            return

        # Initialize Pygame
        pygame.init()

        # Initialize Game Screen
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Snake Game')

        # Load splash screen image
        self.splash_image = pygame.image.load('snake.png')
        self.splash_image = pygame.transform.scale(self.splash_image, (self.WIDTH, self.HEIGHT))

        # Load background image
        try:
            self.background = pygame.image.load('game_bg.png')
            self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))
        except pygame.error as e:
            print(f"Error loading background image: {e}")
            self.background = None

        # Clock for controlling speed
        self.clock = pygame.time.Clock()

        # Game States
        self.snake_pos = (100, 50)
        self.snake_body = [(100, 50), (90, 50), (80, 50)]
        self.snake_direction = 'RIGHT'
        self.change_direction = self.snake_direction
        self.food_pos = (random.randrange(1, (self.WIDTH // self.SNAKE_SIZE)) * self.SNAKE_SIZE,
                         random.randrange(1, (self.HEIGHT // self.SNAKE_SIZE)) * self.SNAKE_SIZE)
        self.food_spawn = True
        self.other_players = {}
        self.running = True
        self.score = 0  # Initialize score

    def reset_game(self):
        self.snake_pos = (self.WIDTH // 2, self.HEIGHT // 2)
        self.snake_body = [self.snake_pos, (self.snake_pos[0] - self.SNAKE_SIZE, self.snake_pos[1]), 
                           (self.snake_pos[0] - 2 * self.SNAKE_SIZE, self.snake_pos[1])]
        self.snake_direction = 'RIGHT'
        self.change_direction = self.snake_direction
        self.spawn_food()

    def spawn_food(self):
        self.food_pos = (
            random.randrange(self.BORDER_OFFSET // self.SNAKE_SIZE, 
                             (self.WIDTH - self.BORDER_OFFSET) // self.SNAKE_SIZE) * self.SNAKE_SIZE,
            random.randrange(self.BORDER_OFFSET // self.SNAKE_SIZE, 
                             (self.HEIGHT - self.BORDER_OFFSET) // self.SNAKE_SIZE) * self.SNAKE_SIZE
        )
        self.food_spawn = True

    def show_start_screen(self):
        self.screen.blit(self.splash_image, (0, 0))
        self.draw_text('Press SPACE to start or ESC to quit', 35, self.GREEN, self.WIDTH / 2, self.HEIGHT - 50)
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
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key in keys:
                        if event.key == pygame.K_SPACE:
                            waiting = False
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
                            waiting = False

    def game_over(self):
        self.draw_text('Game Over!', 35, self.RED, self.WIDTH / 2, self.HEIGHT / 4)
        self.draw_text('Press SPACE to restart or ESC to quit', 25, self.RED, self.WIDTH / 2, self.HEIGHT / 4 + 40)
        pygame.display.flip()
        self.wait_for_key([pygame.K_SPACE, pygame.K_ESCAPE])
        if self.running:
            self.reset_game()

    def send_player_data(self):
        while self.running:
            try:
                data = {
                    'position': self.snake_pos,
                    'direction': self.snake_direction
                }
                self.client.send(json.dumps(data).encode('utf-8'))
            except socket.error:
                print("Unable to send data to the server.")
                self.running = False
                break
            time.sleep(0.1)  # Adjust the frequency of sending data

    def receive_player_data(self):
        while self.running:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if data:
                    self.other_players = json.loads(data)  # Update other players' positions
            except socket.timeout:
                continue
            except socket.error:
                print("An error occurred while receiving data!")
                self.client.close()
                self.running = False
                break

    def update_score(self):
        self.score += 10  # Increment score when food is eaten

    def draw_score(self):
        self.draw_text(str(self.score), 25, self.BLACK, self.WIDTH / 2, 5)  # Display score at the top center

    def run(self):
        if not self.running:
            return

        # Thread Setup
        send_thread = threading.Thread(target=self.send_player_data)
        send_thread.daemon = True
        send_thread.start()
        receive_thread = threading.Thread(target=self.receive_player_data)
        receive_thread.daemon = True
        receive_thread.start()

        self.reset_game()
        self.show_start_screen()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_UP and self.snake_direction != 'DOWN':
                        self.change_direction = 'UP'
                    if event.key == pygame.K_DOWN and self.snake_direction != 'UP':
                        self.change_direction = 'DOWN'
                    if event.key == pygame.K_LEFT and self.snake_direction != 'RIGHT':
                        self.change_direction = 'LEFT'
                    if event.key == pygame.K_RIGHT and self.snake_direction != 'LEFT':
                        self.change_direction = 'RIGHT'

            self.snake_direction = self.change_direction

            # Move snake
            if self.snake_direction == 'UP':
                self.snake_pos = (self.snake_pos[0], self.snake_pos[1] - self.SNAKE_SIZE)
            if self.snake_direction == 'DOWN':
                self.snake_pos = (self.snake_pos[0], self.snake_pos[1] + self.SNAKE_SIZE)
            if self.snake_direction == 'LEFT':
                self.snake_pos = (self.snake_pos[0] - self.SNAKE_SIZE, self.snake_pos[1])
            if self.snake_direction == 'RIGHT':
                self.snake_pos = (self.snake_pos[0] + self.SNAKE_SIZE, self.snake_pos[1])

            # Snake growing logic
            self.snake_body.insert(0, self.snake_pos)
            if self.snake_pos == self.food_pos:
                self.food_spawn = False
                self.update_score()  # Update score when food is eaten
            else:
                self.snake_body.pop()

            # Spawn new food if eaten
            if not self.food_spawn:
                self.food_pos = (random.randrange(1, (self.WIDTH // self.SNAKE_SIZE)) * self.SNAKE_SIZE,
                                random.randrange(1, (self.HEIGHT // self.SNAKE_SIZE)) * self.SNAKE_SIZE)
                self.food_spawn = True

            # Clear screen and draw snake, food, and score
            self.screen.fill(self.BLACK)
            if self.background:
                self.screen.blit(self.background, (0, 0))  # Draw the background image first
            else:
                self.screen.fill(self.BLACK)  # Fallback to black if image not loaded

            for part in self.snake_body:
                pygame.draw.rect(self.screen, self.GREEN, (part[0], part[1], self.SNAKE_SIZE, self.SNAKE_SIZE))
            pygame.draw.rect(self.screen, self.RED, (self.food_pos[0], self.food_pos[1], self.SNAKE_SIZE, self.SNAKE_SIZE))

            # Draw other players
            for player_data in self.other_players.values():
                player_pos = player_data['position']
                pygame.draw.rect(self.screen, self.WHITE, (player_pos[0], player_pos[1], self.SNAKE_SIZE, self.SNAKE_SIZE))

            self.draw_score()  # Draw the score on the screen after the background

            # Draw borders
            pygame.draw.rect(self.screen, self.WHITE, (self.BORDER_OFFSET, self.BORDER_OFFSET, 
                                                       self.WIDTH - 2 * self.BORDER_OFFSET, 
                                                       self.HEIGHT - 2 * self.BORDER_OFFSET), 1)

            # Check for collisions with boundaries or self, considering border offsets
            if (self.snake_pos[0] < self.BORDER_OFFSET or self.snake_pos[0] >= self.WIDTH - self.BORDER_OFFSET or
                    self.snake_pos[1] < self.BORDER_OFFSET or self.snake_pos[1] >= self.HEIGHT - self.BORDER_OFFSET or
                    self.snake_body[0] in self.snake_body[1:]):
                self.game_over()

            pygame.display.update()
            self.clock.tick(self.FPS)

        pygame.quit()
        try:
            self.client.close()
        except:
            pass

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
