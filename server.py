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

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, server_port))
server.listen()

clients = []  # List of client sockets
players = []  # List of player names ("Player 1", "Player 2", etc.)
positions = []  # List of player positions

def handle_client(client, addr):
    global positions, players
    print(f"Connected with {addr}")

    # Assign a new player name based on the number of clients connected
    player_name = f"Player {len(clients) + 1}"
    clients.append(client)
    players.append(player_name)
    positions.append(None)  # Placeholder for player position

    print(f"{player_name} has joined. Players: {players}")

    broadcast_clients()  # Send the updated player list to all clients

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                # Update player position from the message
                data = json.loads(message)
                print(f"Received data from {player_name}: {data}")  # Debug message

                # Update the position for this player (find the index based on the client socket)
                index = clients.index(client)
                positions[index] = data  # Update position at the corresponding index

                broadcast_positions()  # Broadcast updated positions to all clients
        except Exception as exception:
            print(f"Error with {player_name}: {exception}")
            index = clients.index(client)

            clients.pop(index)
            players.pop(index)
            positions.pop(index)  # Remove the position when the player disconnects
            client.close()

            broadcast_clients()  # Update the client list
            break

def broadcast_positions():
    # Prepare a list of positions to broadcast
    player_positions = {players[i]: positions[i] for i in range(len(players)) if positions[i] is not None}
    
    # Send the updated positions to all clients
    for client in clients:
        try:
            client.send(json.dumps(player_positions).encode('utf-8'))
            print(f"Broadcasting positions: {player_positions}")
        except:
            clients.remove(client)

def broadcast_clients():
    # Send the updated player list (with player names) to all clients
    for client in clients:
        try:
            client.send(json.dumps({"players": players}).encode('utf-8'))
            print(f"Broadcasting clients: {players}")
        except:
            clients.remove(client)

def start():
    print("Server is running...")
    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

start()
