import socket
import threading
import json
import pika

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 3001

connected_clients = []
chat_rooms = {}
rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters(SERVER_HOST))
rabbit_channel = rabbit_connection.channel()
rabbit_channel.queue_declare(queue='chat_message')

def create_json_message(msg_type, content):
    return json.dumps({"type": msg_type, "content": content})
def send_to_clients(ch, method, properties, body):
    message_content = json.loads(body)
    target_room = message_content["content"]["room"]
    room_clients = chat_rooms.get(target_room, [])

    outgoing_msg = create_json_message("chat", {
        "user": message_content["content"]["user"],
        "room": target_room,
        "message": message_content["content"]["message"]
    })

    print(f"Sending to {target_room} by {message_content['content']['user']}: {message_content['content']['message']}")
    for client in room_clients:
        client.send(outgoing_msg.encode('utf-8'))

    ch.basic_ack(delivery_tag=method.delivery_tag)
def begin_consume():
    rabbit_channel.basic_consume(queue='chat_message', on_message_callback=send_to_clients, auto_ack=False)
    rabbit_channel.start_consuming()

consume_thread = threading.Thread(target=begin_consume, daemon=True)
consume_thread.start()
def client_interaction(client, address):
    global connected_clients, chat_rooms
    user_name = ""
    user_room = ""

    while True:
        try:
            msg_json = client.recv(1024).decode('utf-8')
            if not msg_json:
                break

            msg_data = json.loads(msg_json)
            if msg_data["type"] == "join":
                user_name = msg_data["content"]["user"]
                user_room = msg_data["content"]["room"]
                room_clients = chat_rooms.get(user_room, [])
                room_clients.append(client)
                chat_rooms[user_room] = room_clients
                join_ack = create_json_message("join_ack", {"text": "You've joined the chat room."})
                client.send(join_ack.encode('utf-8'))

                notification_msg = create_json_message("notify", {"text": f"{user_name} entered the chat room."})
                for conn_client in room_clients:
                    if conn_client != client:
                        conn_client.send(notification_msg.encode('utf-8'))

            elif msg_data["type"] == "chat":
                rabbit_channel.basic_publish(
                    exchange='',
                    routing_key='chat_message',
                    body=json.dumps(msg_data),
                    properties=pika.BasicProperties(delivery_mode=2))

        except json.JSONDecodeError:
            continue

    connected_clients.remove(client)
    if user_room in chat_rooms:
        chat_rooms[user_room].remove(client)
    client.close()

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen()

    try:
        while True:
            client_sock, client_addr = server.accept()
            connected_clients.append(client_sock)
            threading.Thread(target=client_interaction, args=(client_sock, client_addr)).start()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        rabbit_channel.stop_consuming()
        rabbit_connection.close()
