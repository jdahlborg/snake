import logging
import queue
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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((server_ip, server_port))
    server.listen()

    clients = queue.Queue()  # Thread-safe queue for client sockets
    players = queue.Queue()  # Thread-safe queue for player names ("Player 1", "Player 2", etc.)
    positions = queue.Queue()  # Thread-safe queue for player positions

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    def handle_client(client, addr):
        global positions, players
        logger.info(f"Connected with {addr}")

        # Assign a new player name based on the number of clients connected
        player_name = f"Player {clients.qsize() + 1}"
        clients.put(client)
        players.put(player_name)
        positions.put(None)  # Placeholder for player position

        logger.info(f"{player_name} has joined. Players: {list(players.queue)}")

        broadcast_clients()  # Send the updated player list to all clients

        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message:
                    # Update player position from the message
                    data = json.loads(message)
                    logger.info(f"Received data from {player_name}: {data}")  # Debug message

                    # Update the position for this player (find the index based on the client socket)
                    index = list(clients.queue).index(client)
                    positions.queue[index] = data  # Update position at the corresponding index

                    broadcast_positions()  # Broadcast updated positions to all clients
            except Exception as exception:
                logger.error(f"Error with {player_name}: {exception}")
                index = list(clients.queue).index(client)

                clients.queue.remove(client)
                players.queue.remove(player_name)
                positions.queue.remove(positions.queue[index])  # Remove the position when the player disconnects
                client.close()

                broadcast_clients()  # Update the client list
                break

    def broadcast_positions():
        # Prepare a list of positions to broadcast
        player_positions = {list(players.queue)[i]: list(positions.queue)[i] for i in range(len(list(players.queue))) if list(positions.queue)[i] is not None}
        
        # Send the updated positions to all clients
        for client in list(clients.queue):
            if client in clients.queue:  # Check if client is still in the queue
                try:
                    client.send(json.dumps(player_positions).encode('utf-8'))
                    logger.info(f"Broadcasting positions: {player_positions}")
                except:
                    clients.queue.remove(client)

    def broadcast_clients():
        # Send the updated player list (with player names) to all clients
        for client in list(clients.queue):
            if client in clients.queue:  # Check if client is still in the queue
                try:
                    client.send(json.dumps({"players": list(players.queue)}).encode('utf-8'))
                    logger.info(f"Broadcasting clients: {list(players.queue)}")
                except:
                    clients.queue.remove(client)

    def start():
        logger.info("Server is running...")
        while True:
            client, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.start()

    start()