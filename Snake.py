import pygame
import random
import socket
import threading
import json
import time

# Socket setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('10.80.207.104', 5555))

# Initialize Pygame
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

# Player state
snake_pos = (100, 50)
snake_body = [(100, 50), (90, 50), (80, 50)]
snake_direction = 'RIGHT'
change_direction = snake_direction
food_pos = (random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
            random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE)
food_spawn = True

# Store positions of other players
other_players = {}

def reset_game():
    global snake_pos, snake_body, snake_direction, change_direction, food_pos, food_spawn
    snake_pos = (100, 50)
    snake_body = [(100, 50), (90, 50), (80, 50)]
    snake_direction = 'RIGHT'
    change_direction = snake_direction
    food_pos = (random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
                random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE)
    food_spawn = True

def show_start_screen():
    font = pygame.font.SysFont('arial', 35)
    start_surface = font.render('Press SPACE to start or ESC to quit', True, GREEN)
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
                if event.key == pygame.K_SPACE:  # Start the game when SPACE is pressed
                    waiting = False
                if event.key == pygame.K_ESCAPE:  # Quit the game when ESC is pressed
                    pygame.quit()
                    quit()

def game_over():
    font = pygame.font.SysFont('arial', 35)
    game_over_surface = font.render('Game Over! Press SPACE to restart or ESC to quit', True, RED)
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
                if event.key == pygame.K_SPACE:  # Reset the game when SPACE is pressed
                    waiting = False
                    reset_game()
                if event.key == pygame.K_ESCAPE:  # Quit the game when ESC is pressed
                    pygame.quit()
                    quit()




# Send player's position and direction to the server
def send_player_data():
    while True:
        data = {
            'position': snake_pos,
            'direction': snake_direction
        }
        client.send(json.dumps(data).encode('utf-8'))
        time.sleep(0.1)  # Adjust the frequency of sending data

# Receive other players' positions from the server
def receive_player_data():
    global other_players
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            if data:
                other_players = json.loads(data)  # Update other players' positions
        except:
            print("An error occurred while receiving data!")
            client.close()
            break

# Start the threads to send and receive player data
send_thread = threading.Thread(target=send_player_data)
send_thread.start()
receive_thread = threading.Thread(target=receive_player_data)
receive_thread.start()

# Main Game Loop
reset_game()  # Initialize game state
show_start_screen()  # Show the start screen before starting

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Exit the game when Esc is pressed
                running = False
            if event.key == pygame.K_UP and snake_direction != 'DOWN':
                change_direction = 'UP'
            if event.key == pygame.K_DOWN and snake_direction != 'UP':
                change_direction = 'DOWN'
            if event.key == pygame.K_LEFT and snake_direction != 'RIGHT':
                change_direction = 'LEFT'
            if event.key == pygame.K_RIGHT and snake_direction != 'LEFT':
                change_direction = 'RIGHT'

    snake_direction = change_direction

    # Move snake
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

    # Spawn new food if eaten
    if not food_spawn:
        food_pos = (random.randrange(1, (WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
                    random.randrange(1, (HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE)
        food_spawn = True

    # Clear screen and draw snake and food
    screen.fill(BLACK)
    for part in snake_body:
        pygame.draw.rect(screen, GREEN, (part[0], part[1], SNAKE_SIZE, SNAKE_SIZE))
    pygame.draw.rect(screen, RED, (food_pos[0], food_pos[1], SNAKE_SIZE, SNAKE_SIZE))

    # Draw other players (if implemented)
    for addr, player_data in other_players.items():
        player_pos = player_data['position']
        pygame.draw.rect(screen, WHITE, (player_pos[0], player_pos[1], SNAKE_SIZE, SNAKE_SIZE))

    # Check for collisions with boundaries or self
    if (snake_pos[0] < 0 or snake_pos[0] >= WIDTH or
            snake_pos[1] < 0 or snake_pos[1] >= HEIGHT or
            snake_body[0] in snake_body[1:]):
        game_over()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
client.close()
