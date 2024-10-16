import logging
import socket
from dotenv import load_dotenv
import os
import threading
import json

# Load environment variables from .env file
load_dotenv()

# Get the server IP and port from environment variables
server_ip = os.getenv('SERVER_IP', '127.0.0.1')  # Default to 127.0.0.1 if not set
server_port = int(os.getenv('SERVER_PORT', 5555))  # Default to 5555 if not set

# Initialize global variables
player_positions = {}
active_clients = []

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

def handle_client(client, addr):
    global active_clients  # Declare as global to modify
    logger.info(f"Connected with {addr}")

    # Assign a new player name based on the number of clients connected
    player_name = f"Player {len(active_clients) + 1}"

    active_clients.append(client)
    player_positions[player_name] = None  # Placeholder for player position

    logger.info(f"{player_name} has joined. Players: {list(player_positions.keys())}")

    broadcast_clients()  # Send the updated player list to all clients

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                # Update player position from the message
                data = json.loads(message)
                logger.info(f"Received data from {player_name}: {data}")  # Debug message

                # Update the position for this player
                player_positions[player_name] = data

                broadcast_positions()  # Broadcast updated positions to all clients
        except ConnectionResetError:
            logger.error(f"Connection reset by peer: {player_name}")
            break
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {player_name}")
            break
        except Exception as exception:
            logger.error(f"Error with {player_name}: {exception}")
            break

    # Remove the client from active clients and player positions
    active_clients.remove(client)
    del player_positions[player_name]

    client.close()

    broadcast_clients()  # Update the client list

def broadcast_positions():
    # Send the updated positions to all clients
    for client in active_clients:
        try:
            json_data = json.dumps(player_positions)
            client.sendall(json_data.encode('utf-8') + b'\n')  # Add newline as a delimiter
        except ConnectionError:
            logger.error(f"Connection error while broadcasting positions")


def broadcast_clients():
    # Send the updated player list (with player names) to all clients
    for client in active_clients:
        try:
            client.send(json.dumps({"players": list(player_positions.keys())}).encode('utf-8'))
            logger.info(f"Broadcasting clients: {list(player_positions.keys())}")
        except ConnectionError:
            logger.error(f"Connection error while broadcasting clients")

def start():
    logger.info("Server is running...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((server_ip, server_port))
        server.listen()
        while True:
            client, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.start()

start()
