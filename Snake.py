import pygame
import random
import socket
import threading

# Network setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('10.80.207.104', 5555))  # Replace with your server IP

# Function to receive messages from the server
def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)  # Handle incoming messages here
        except:
            print("An error occurred!")
            client.close()
            break

# Function to send messages to the server
def send(message):
    client.send(message.encode('utf-8'))

# Start the receive thread
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Pygame setup
pygame.init()

# Game Constants
WIDTH, HEIGHT = 640, 480
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

# Define function to reset the game state
def reset_game():
    global snake_pos, snake_body, snake_direction, change_direction, food_pos, food_spawn, FPS, initial_length, snake_set
    snake_pos = (100, 50)
    snake_body = [(100, 50), (90, 50), (80, 50)]
    snake_set = set(snake_body)  # For faster collision detection
    snake_direction = 'RIGHT'
    change_direction = snake_direction
    food_pos = get_new_food_pos()
    food_spawn = True
    FPS = 15  # Reset speed
    initial_length = len(snake_body)

# Function to show the start screen
def show_start_screen():
    font = pygame.font.SysFont('arial', 35)
    start_surface = font.render('Press any key to start', True, GREEN)
    start_rect = start_surface.get_rect()
    start_rect.midtop = (WIDTH / 2, HEIGHT / 2)
    screen.fill(BLACK)
    screen.blit(start_surface, start_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Show the game over screen and wait for restart
def game_over():
    font = pygame.font.SysFont('arial', 35)
    game_over_surface = font.render('Game Over! Press any key to restart', True, RED)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (WIDTH / 2, HEIGHT / 4)
    screen.fill(BLACK)
    screen.blit(game_over_surface, game_over_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False
                reset_game()  # Reset the game state to restart

# Optimized food spawning to avoid checking the entire snake body
def get_new_food_pos():
    while True:
        food_x = random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE
        food_y = random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE
        if (food_x, food_y) not in snake_set:
            return (food_x, food_y)

# Main Game Loop
reset_game()  # Initialize game state
show_start_screen()  # Show the start screen before starting

running = True
while running:
    # Handle events and direction changes
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_direction != 'DOWN':
                change_direction = 'UP'
                send('UP')  # Send direction change to the server
            if event.key == pygame.K_DOWN and snake_direction != 'UP':
                change_direction = 'DOWN'
                send('DOWN')
            if event.key == pygame.K_LEFT and snake_direction != 'RIGHT':
                change_direction = 'LEFT'
                send('LEFT')
            if event.key == pygame.K_RIGHT and snake_direction != 'LEFT':
                change_direction = 'RIGHT'
                send('RIGHT')

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
    snake_set.add(snake_pos)

    if snake_pos == food_pos:
        food_spawn = False
    else:
        snake_set.remove(snake_body.pop())  # Remove the tail from set and list

    # Spawn new food if eaten
    if not food_spawn:
        food_pos = get_new_food_pos()
        food_spawn = True

    # Clear screen and draw snake and food
    screen.fill(BLACK)
    for part in snake_body:
        pygame.draw.rect(screen, GREEN, (part[0], part[1], SNAKE_SIZE, SNAKE_SIZE))
    pygame.draw.rect(screen, RED, (food_pos[0], food_pos[1], SNAKE_SIZE, SNAKE_SIZE))

    # Check for collisions with boundaries or self
    if (snake_pos[0] < 0 or snake_pos[0] >= WIDTH or
            snake_pos[1] < 0 or snake_pos[1] >= HEIGHT or
            snake_body[0] in snake_body[1:]):
        game_over()

    # Increase speed every time the snake length grows by 5
    if (len(snake_body) - initial_length) % 5 == 0 and len(snake_body) > initial_length:
        FPS += 1
        initial_length = len(snake_body)  # Update initial length to the new value

    # Update the display and set the speed of the game
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
client.close()
