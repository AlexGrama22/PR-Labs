import socket
import threading
import json
import os
import uuid

HOST = '127.0.0.1'
PORT = 3001
client_id = str(uuid.uuid4())
CLIENT_DIR = os.path.join('Downloads', client_id)

os.makedirs(CLIENT_DIR, exist_ok=True)


def receive_messages():
    file_name = None
    is_file = False
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                print("Connection lost.")
                break

            if is_file:
                with open(os.path.join(CLIENT_DIR, file_name), 'ab') as file:
                    file.write(message)

                    while True:
                        client_socket.settimeout(0.5)
                        try:
                            next_chunk = client_socket.recv(1024)
                            if not next_chunk:
                                break
                            file.write(next_chunk)
                        except socket.timeout:
                            break

                print(f"File {file_name} has been downloaded successfully to {os.path.join(CLIENT_DIR, file_name)}.")
                file_name = None
                is_file = False
                client_socket.settimeout(None)
                continue

            message_str = message.decode('utf-8', errors='ignore')

            if message_str.strip().startswith('{') and message_str.strip().endswith('}'):
                message_json = json.loads(message_str)
                msg_type = message_json.get('type')

                if msg_type == 'file_info':
                    file_name = message_json['payload']['name']
                    is_file = True
                elif msg_type == 'notification':
                    print(message_json['payload']['message'])
                elif msg_type == 'message':
                    payload = message_json['payload']
                    print(f"{payload['sender']}: {payload['text']}")
                elif msg_type == 'connect_ack':
                    print(message_json['payload']['message'])
                elif msg_type == 'error':
                    print(message_json['payload']['message'])

        except Exception as e:
            print(f"Error occurred: {e}")
            break

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")

name = input("Enter your name: ").strip()
room = input("Enter the room you want to join: ").strip()

connect_msg = {
    "type": "connect",
    "payload": {"name": name, "room": room}
}
client_socket.send(json.dumps(connect_msg).encode('utf-8'))

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

try:
    while True:
        text = input()
        if text.lower() == 'exit':
            break
        elif text.lower().startswith('upload:'):
            _, file_path = text.split(':', 1)
            message = {
                "type": "upload",
                "payload": {"path": file_path.strip()}
            }
        elif text.lower().startswith('download:'):
            _, file_name = text.split(':', 1)
            message = {
                "type": "download",
                "payload": {"name": file_name.strip()}
            }
        else:
            message = {
                "type": "message",
                "payload": {"sender": name, "room": room, "text": text}
            }

        client_socket.send(json.dumps(message).encode('utf-8'))
except KeyboardInterrupt:
    print("\nExiting the client.")
finally:
    client_socket.close()