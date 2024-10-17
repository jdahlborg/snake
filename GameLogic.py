import pygame
import random

class GameLogic:
    def __init__(self):
        # Initialize game state variables
        self.snake_pos = (100, 50)
        self.snake_body = [(100, 50), (90, 50), (80, 50)]
        self.snake_direction = 'RIGHT'
        self.change_direction = self.snake_direction
        self.food_pos = (0, 0)
        self.food_spawn = True
        self.running = True
        self.score = 0
        self.fruits_eaten = 0
        self.FPS = 15
        self.clock = pygame.time.Clock()

    def reset_game(self):
        # Reset game states
        self.snake_pos = (320, 240)
        self.snake_body = [self.snake_pos, (self.snake_pos[0] - 10, self.snake_pos[1]), 
                           (self.snake_pos[0] - 20, self.snake_pos[1])]
        self.snake_direction = 'RIGHT'
        self.change_direction = self.snake_direction
        self.score = 0 
        self.fruits_eaten = 0
        self.spawn_food()

    def handle_events(self):
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

    def update_game_state(self):
        self.snake_direction = self.change_direction
        # Move snake
        if self.snake_direction == 'UP':
            self.snake_pos = (self.snake_pos[0], self.snake_pos[1] - 10)
        if self.snake_direction == 'DOWN':
            self.snake_pos = (self.snake_pos[0], self.snake_pos[1] + 10)
        if self.snake_direction == 'LEFT':
            self.snake_pos = (self.snake_pos[0] - 10, self.snake_pos[1])
        if self.snake_direction == 'RIGHT':
            self.snake_pos = (self.snake_pos[0] + 10, self.snake_pos[1])

        # Snake growing logic
        self.snake_body.insert(0, self.snake_pos)
        if self.snake_pos == self.food_pos:
            self.food_spawn = False
            self.update_score()
        else:
            self.snake_body.pop()

        # Spawn new food if eaten
        if not self.food_spawn:
            self.spawn_food()

        # Check for collisions
        if (self.snake_pos[0] < 70 or self.snake_pos[0] >= 640 - 70 or
                self.snake_pos[1] < 70 or self.snake_pos[1] >= 480 - 70 or
                self.snake_body[0] in self.snake_body[1:]):
            self.running = False

        self.clock.tick(self.FPS)

    def spawn_food(self):
        while True:
            food_pos = (
                random.randrange(7, 57) * 10,
                random.randrange(7, 37) * 10
            )
            if food_pos not in self.snake_body:
                break
        self.food_pos = food_pos
        self.food_spawn = True

    def update_score(self):
        self.score += 10
        self.fruits_eaten += 1
        if self.fruits_eaten % 5 == 0:
            self.FPS += 2
