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

# Initial snake setup
snake_pos = (100, 50)
snake_body = [(100, 50), (90, 50), (80, 50)]  # List of tuples for the snake body
snake_direction = 'RIGHT'
change_direction = snake_direction
initial_length = len(snake_body)

# Food setup
food_pos = (random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
            random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE)
food_spawn = True

def game_over():
    font = pygame.font.SysFont('arial', 35)
    game_over_surface = font.render('Game Over', True, RED)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (WIDTH / 2, HEIGHT / 4)
    screen.fill(BLACK)
    screen.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    pygame.time.wait(2000)  # Wait for 2 seconds before quitting
    pygame.quit()
    quit()

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

    # Snake growing logic
    snake_body.insert(0, snake_pos)
    if snake_pos == food_pos:
        food_spawn = False
    else:
        snake_body.pop()

    # Spawn food again, ensuring it doesn't spawn on the snake
    if not food_spawn:
        while food_pos in snake_body:
            food_pos = (random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
                        random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE)
    food_spawn = True

    # Clear screen and draw snake and food
    screen.fill(BLACK)
    for part in snake_body:
        pygame.draw.rect(screen, GREEN, pygame.Rect(part[0], part[1], SNAKE_SIZE, SNAKE_SIZE))
    pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], SNAKE_SIZE, SNAKE_SIZE))

    # Check for collisions with boundaries
    if (snake_pos[0] < 0 or snake_pos[0] >= WIDTH or
            snake_pos[1] < 0 or snake_pos[1] >= HEIGHT):
        game_over()

    # Check for collisions with self
    for block in snake_body[1:]:
        if snake_pos == block:
            game_over()

    # Increase speed every time the snake length grows by 5
    if (len(snake_body) - initial_length) % 5 == 0 and len(snake_body) > initial_length:
        FPS += 1
        initial_length = len(snake_body)  # Update initial length to the new value

    # Update the display and set the speed of the game
    pygame.display.update()
    clock.tick(FPS)
