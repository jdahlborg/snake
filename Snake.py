import pygame
import random

pygame.init()

# Game Constants
WIDTH, HEIGHT = 600, 400
SNAKE_SIZE = 10
FPS = 15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Initialize Game Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')

# Clock for controlling speed
clock = pygame.time.Clock()

# Initial snake setup (now using tuples for positions)
snake_pos = (100, 50)  # Tuple for (x, y)
snake_body = [(100, 50), (90, 50), (80, 50)]  # List of tuples for the snake body
snake_direction = 'RIGHT'
change_direction = snake_direction

# Food setup (using tuple)
food_pos = (random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
            random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE)
food_spawn = True

# Main Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_direction != 'DOWN':
                change_direction = 'UP'
            if event.key == pygame.K_DOWN and snake_direction != 'UP':
                change_direction = 'DOWN'
            if event.key == pygame.K_LEFT and snake_direction != 'RIGHT':
                change_direction = 'LEFT'
            if event.key == pygame.K_RIGHT and snake_direction != 'LEFT':
                change_direction = 'RIGHT'

    snake_direction = change_direction

    # Move snake (using tuples for the position)
    if snake_direction == 'UP':
        snake_pos = (snake_pos[0], snake_pos[1] - SNAKE_SIZE)
    if snake_direction == 'DOWN':
        snake_pos = (snake_pos[0], snake_pos[1] + SNAKE_SIZE)
    if snake_direction == 'LEFT':
        snake_pos = (snake_pos[0] - SNAKE_SIZE, snake_pos[1])
    if snake_direction == 'RIGHT':
        snake_pos = (snake_pos[0] + SNAKE_SIZE, snake_pos[1])

    # Snake growing logic (append new head as tuple)
    snake_body.insert(0, snake_pos)
    if snake_pos == food_pos:
        food_spawn = False
    else:
        snake_body.pop()  # Remove last segment

    # Spawn food again
    if not food_spawn:
        food_pos = (random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
                    random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE)
    food_spawn = True

    # Clear screen and draw snake and food
    screen.fill(BLACK)
    for part in snake_body:
        pygame.draw.rect(screen, GREEN, pygame.Rect(part[0], part[1], SNAKE_SIZE, SNAKE_SIZE))
    pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], SNAKE_SIZE, SNAKE_SIZE))

    # Check for collisions
    if (snake_pos[0] < 0 or snake_pos[0] >= WIDTH or
            snake_pos[1] < 0 or snake_pos[1] >= HEIGHT):
        pygame.quit()
        quit()

    for block in snake_body[1:]:
        if snake_pos == block:
            pygame.quit()
            quit()

    # Update the display and set the speed of the game
    pygame.display.update()
    clock.tick(FPS)
