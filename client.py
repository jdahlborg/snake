import pygame
import socketio
import sys
import traceback
import time

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
SNAKE_SIZE = 10
FOOD_SIZE = 10
FPS = 10

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

class SnakeGame:
    def __init__(self):
        print("Initializing SnakeGame...")
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Multiplayer Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        print("Initializing Socket.IO client...")
        self.sio = socketio.Client()
        self.setup_socketio_events()

        self.players = {}
        self.food_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.snake_pos = [100, 50]
        self.snake_body = [self.snake_pos[:]]
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.speed = 10

        self.running = False
        print("SnakeGame initialized.")

    def setup_socketio_events(self):
        @self.sio.event
        def connect():
            print("Connected to server")

        @self.sio.event
        def connect_error(data):
            print("Failed to connect to server:", data)

        @self.sio.event
        def disconnect():
            print("Disconnected from server")

        @self.sio.event
        def init(data):
            self.food_pos = data['food_pos']
            self.players = data['players']
            print("Received initial data from server:", data)

        @self.sio.event
        def update_players(data):
            self.players = data
            #print("Updated players data:", data)

        @self.sio.event
        def new_food(data):
            self.food_pos = data
            print("New food position received:", data)

    def connect_to_server(self):
        while not self.sio.connected:
            try:
                print("Attempting to connect to server...")
                self.sio.connect('http://127.0.0.1:5001')
                #self.sio.connect('http://10.80.207.104:5555')
                print("Successfully connected to server")
            except Exception as e:
                print(f"Failed to connect to server: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)  # Wait before retrying

    def show_message(self, message):
        self.screen.fill(WHITE)
        text = self.font.render(message, True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    # Rotate direction counter-clockwise
                    self.change_to = {'UP': 'LEFT', 'LEFT': 'DOWN', 'DOWN': 'RIGHT', 'RIGHT': 'UP'}[self.direction]
                elif event.key == pygame.K_RIGHT:
                    # Rotate direction clockwise
                    self.change_to = {'UP': 'RIGHT', 'RIGHT': 'DOWN', 'DOWN': 'LEFT', 'LEFT': 'UP'}[self.direction]
        return True

    def move_snake(self):
        if self.change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        if self.change_to == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'
        if self.change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        if self.change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'

        if self.direction == 'UP':
            self.snake_pos[1] -= self.speed
        if self.direction == 'DOWN':
            self.snake_pos[1] += self.speed
        if self.direction == 'LEFT':
            self.snake_pos[0] -= self.speed
        if self.direction == 'RIGHT':
            self.snake_pos[0] += self.speed

        # Wrap the snake around the screen
        self.snake_pos[0] %= SCREEN_WIDTH
        self.snake_pos[1] %= SCREEN_HEIGHT

        # Add new head to the snake body
        self.snake_body.insert(0, list(self.snake_pos))
        if self.snake_pos == self.food_pos:
            self.sio.emit('eat_food')
        else:
            self.snake_body.pop()

    def draw_elements(self):
        self.screen.fill(WHITE)
        for pos in self.snake_body:
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(pos[0], pos[1], SNAKE_SIZE, SNAKE_SIZE))
        pygame.draw.rect(self.screen, RED, pygame.Rect(self.food_pos[0], self.food_pos[1], FOOD_SIZE, FOOD_SIZE))
        pygame.display.flip()

    def run(self):
        self.connect_to_server()  # Attempt to connect to the server
        while True:
            if self.sio.connected:
                self.running = self.handle_input()
                if not self.running:
                    break
                self.move_snake()
                self.sio.emit('move', {'pos': self.snake_pos, 'body': self.snake_body, 'direction': self.direction})
                self.draw_elements()
            else:
                print("Not connected to server, attempting to reconnect...")
                self.connect_to_server()
            self.clock.tick(FPS)

    def cleanup(self):
        print("Cleaning up...")
        if self.sio.connected:
            self.sio.disconnect()
        pygame.quit()
        print("Cleanup complete.")

if __name__ == "__main__":
    game = SnakeGame()
    try:
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Traceback:")
        traceback.print_exc()
    finally:
        game.cleanup()
        print("Game exited.")
