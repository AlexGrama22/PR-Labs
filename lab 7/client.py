import pika
import threading
import json

HOST = '127.0.0.1'
PORT = 3001
exqueue = 'chtaexchange'

def receive_messages(ch, method, properties, body):
    message = json.loads(body)
    if message['payload']['sender'] != name:
        print('\r', end='')  # Clear the current line
        print(f"{message['payload']['sender']}: {message['payload']['text']}")
        print(f"{name}: ", end='', flush=True)

def listen_for_messages():
    channel.queue_bind(exchange=exqueue, queue=queue_name, routing_key=room)
    channel.basic_consume(queue=queue_name, on_message_callback=receive_messages, auto_ack=True)
    channel.start_consuming()

name = input("username: ")
room = input("room: ")

connection = pika.BlockingConnection(pika.ConnectionParameters(HOST))
channel = connection.channel()
channel.exchange_declare(exchange=exqueue, exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

# Start the listening thread
listening_thread = threading.Thread(target=listen_for_messages, daemon=True)
listening_thread.start()

try:
    while True:
        text = input(f"{name}: ").strip()
        if text.lower() == 'exit':
            break

        message = {
            "type": "message",
            "payload": {"sender": name, "room": room, "text": text}
        }

        channel.basic_publish(
            exchange=exqueue,
            routing_key=room,
            body=json.dumps(message)
        )
except KeyboardInterrupt:
    print("Closing the connection...")
finally:
    channel.stop_consuming()
    connection.close()