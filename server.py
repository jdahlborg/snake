import socketio
import random

# Create a Socket.IO server instance
sio = socketio.Server()
app = socketio.WSGIApp(sio)

# Game state: Dictionary to store players' positions
players = {}
food_pos = [random.randint(0, 590), random.randint(0, 390)]  # Initial food position

# Handle a new client connection
@sio.event
def connect(sid, environ):
    print(f"New player connected: {sid}")
    sio.emit('init', {'food_pos': food_pos, 'players': players}, to=sid)

# Handle player disconnection
@sio.event
def disconnect(sid):
    print(f"Player {sid} disconnected")
    if sid in players:
        del players[sid]
    sio.emit('update_players', players)

# Handle player movement
@sio.event
def move(sid, data):
    try:
        players[sid] = data  # Update player's position
        sio.emit('update_players', players)  # Broadcast updated game state to all clients
    except Exception as e:
        print(f"Error updating player {sid}: {e}")

# Handle food eaten event and generate new food position
@sio.event
def eat_food(sid):
    global food_pos
    food_pos = [random.randint(0, 590), random.randint(0, 390)]
    sio.emit('new_food', food_pos)

# Run the Socket.IO server using eventlet
if __name__ == '__main__':
    import eventlet
    try:
        eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5001)), app)
    except Exception as e:
        print(f"Server error: {e}")
