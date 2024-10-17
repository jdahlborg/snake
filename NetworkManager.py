import socket
import threading
import json
import os
import time

class NetworkManager:
    def __init__(self, logic):
        self.logic = logic
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(10.0)
        server_ip = os.getenv('SERVER_IP', '127.0.0.1')
        server_port = int(os.getenv('SERVER_PORT', 5555))
        try:
            self.client.connect((server_ip, server_port))
        except socket.error:
            print("Unable to connect to the server.")
            self.logic.running = False

    def start_threads(self):
        send_thread = threading.Thread(target=self.send_player_data)
        send_thread.daemon = True
        send_thread.start()
        receive_thread = threading.Thread(target=self.receive_player_data)
        receive_thread.daemon = True
        receive_thread.start()

    def send_player_data(self):
        while self.logic.running:
            try:
                data = {
                    'position': self.logic.snake_pos,
                    'direction': self.logic.snake_direction
                }
                self.client.send(json.dumps(data).encode('utf-8'))
            except socket.error:
                print("Unable to send data to the server.")
                self.logic.running = False
                break
            time.sleep(0.1)

    def receive_player_data(self):
        buffer = ""
        while self.logic.running:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if data:
                    buffer += data
                    try:
                        self.logic.other_players = json.loads(buffer)
                        buffer = ""
                    except json.JSONDecodeError as e:
                        if "Extra data" in str(e):
                            buffer = buffer.split("}{")[-1]
            except:
                pass

    def close_connection(self):
        try:
            self.client.close()
        except:
            pass
