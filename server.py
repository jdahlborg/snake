import socket
from dotenv import load_dotenv
import os
import threading
import json

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Load environment variables from .env file
load_dotenv()

# Get the server IP and port from environment variables
server_ip = os.getenv('SERVER_IP', '127.0.0.1')  # Default to 127.0.0.1 if not set
server_port = int(os.getenv('SERVER_PORT', 5555))  # Default to 5555 if not set

server.bind((server_ip, server_port))
server.listen()

clients = []
positions = {}  # Store positions of each client

def handle_client(client, addr):
    global positions
    print(f"Connected with {addr}")
    clients.append(client)

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                # Update player position from the message
                data = json.loads(message)
                print (data) #Debug message
                positions[addr] = data  # Update positions dictionary
                broadcast_positions()
        except Exception as e:
            print(f"Error: {e}")
            clients.remove(client)
            del positions[addr]  # Remove player on disconnect
            client.close()
            break

def broadcast_positions():
    # Send the updated positions to all clients
    for client in clients:
        try:
            client.send(json.dumps(positions).encode('utf-8'))
            print(positions)
        except:
            clients.remove(client)

def start():
    print("Server is running...")
    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

start()
