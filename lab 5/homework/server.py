import socket
import threading
import json
import os


HOST = '127.0.0.1'
PORT = 3001
SERVER_MEDIA = 'SERVER_MEDIA'

if not os.path.exists(SERVER_MEDIA):
    os.makedirs(SERVER_MEDIA)

clients = []
rooms = {}


def format_message(msg_type, payload):
    return json.dumps({"type": msg_type, "payload": payload})


def upload_file(client_socket, file_path, client_name):
    if not os.path.exists(file_path):
        error_message = format_message('error', {'message': f"File {file_path} doesn't exist."})
        client_socket.send(error_message.encode('utf-8'))
        return

    with open(file_path, 'rb') as file:
        content = file.read()
        file_name = os.path.basename(file_path)
        server_file_path = os.path.join(SERVER_MEDIA, file_name)

        with open(server_file_path, 'wb') as server_file:
            server_file.write(content)

    notification = format_message("notification", {"message": f"User {client_name} uploaded the {file_name} file."})
    client_socket.send(notification.encode('utf-8'))


def download_file(client_socket, file_name):
    file_path = os.path.join(SERVER_MEDIA, file_name)

    if not os.path.exists(file_path):
        error_message = format_message('error', {'message': f"The {file_name} doesn't exist."})
        client_socket.send(error_message.encode('utf-8'))
        return

    file_info = format_message('file_info', {'name': file_name})
    client_socket.send(file_info.encode('utf-8'))

    with open(file_path, 'rb') as file:
        content = file.read(1024)
        while content:
            client_socket.send(content)
            content = file.read(1024)
def handle_client(client_socket, client_address):
    global clients, rooms
    client_name = ""
    client_room = ""

    while True:
        try:
            message_json = client_socket.recv(1024).decode('utf-8')
            if not message_json:
                break

            message_data = json.loads(message_json)
            print(f"Received: {message_json}")

            if message_data["type"] == "connect":
                client_name = message_data["payload"]["name"]
                client_room = message_data["payload"]["room"]
                clients_in_room = rooms.get(client_room, [])
                clients_in_room.append(client_socket)
                rooms[client_room] = clients_in_room

                ack_message = format_message("connect_ack", {"message": "Connected to the room."})
                client_socket.send(ack_message.encode('utf-8'))
                print(f"{client_name} connected to room {client_room}")

                notification = format_message("notification", {"message": f"{client_name} has joined the room."})
                for client in clients_in_room:
                    if client != client_socket:
                        client.send(notification.encode('utf-8'))

            elif message_data["type"] == "message":
                clients_in_room = rooms.get(client_room, [])
                broadcast_message = format_message("message", {
                    "sender": client_name,
                    "room": client_room,
                    "text": message_data["payload"]["text"]
                })
                print(f"Message in {client_room} from {client_name}: {message_data['payload']['text']}")
                for client in clients_in_room:
                    client.send(broadcast_message.encode('utf-8'))

            elif message_data["type"] == "upload":
                file_path = message_data["payload"]["path"]
                upload_file(client_socket, file_path, client_name)

            elif message_data["type"] == "download":
                file_name = message_data["payload"]["name"]
                download_file(client_socket, file_name)

        except Exception as e:
            print(f"Error occurred: {e}")
            break

    clients.remove(client_socket)
    if client_room in rooms:
        rooms[client_room].remove(client_socket)
    client_socket.close()
    print(f"Connection from {client_address} closed.")


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server is listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            clients.append(client_socket)
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    except KeyboardInterrupt:
        print("Shutting down the server.")
    finally:
        server_socket.close()
