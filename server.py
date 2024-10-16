import socket
import threading
import json

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.bind(('10.80.207.104', 5555))#-
# Replace '10.80.207.104' with the correct IP address#+
server.bind(('10.80.207.104', 5555))
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
        except:
            clients.remove(client)

def start():
    print("Server is running...")
    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

start()
