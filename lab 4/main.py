import socket
import signal
import sys
import json
import re
from time import sleep
import threading

# define the server's IP and port
HOST = "127.0.0.1"
PORT = 4000

# create a socket object ip4, tcp
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen(5)
print(f"[*] Listening as {HOST}:{PORT}")


# Function to handle Ctrl+C and other signals
def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)


# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)


# function to handle clients' requests
def handle_request(client_socket):
    # Receive and print the client's request data
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received Request:\n{request_data}")

    # Parse the request to get the HTTP method and path
    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()

    # Check if the request_line is not empty
    if not request_line:
        print("Empty request received.")
        client_socket.close()
        return

    method = request_line[0]
    path = request_line[1]

    # Initialize the response content and status code
    response_content = ''
    status_code = 200

    with open('products.json', 'r') as file:
        products_data = json.load(file)

    print(products_data)
    # Define a simple routing mechanism
    if path == '/':
        response_content = '<h1>Home</h1>'
        response_content += '<a href="/product">Product</a><br></br>'
        response_content += '<a href="/about">About</a><br></br>'
        response_content += '<a href="/cart">Cart</a>'
    elif path == '/about':
        response_content = '<h1>About</h1>'
    elif path == '/cart':
        response_content = '<h1>Cart</h1>'
    elif path == '/product':
        response_content = '<h1>Product</h1>'
        for item in products_data:
            response_content += '<a href="/product/' + str(item['id']) + '">'+item["name"]+'</a> <br></br>'


    elif re.match('/product/\d+', path):

        product_id = int(path.split('/')[-1])

        product = next((item for item in products_data if item['id'] == product_id), None)  # Look up the product by ID

        if product:
            response_content = f"<h1>{product['name']}</h1>"
            response_content += f"<p>Factory: {product['factory']}</p>"
            response_content += f"<p>Price: ${product['price']}</p>"
            response_content += f"<p>{product['description']}</p>"
        else:
            response_content = '<h1>404 Not Found</h1>'
            status_code = 404

    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content}'
    client_socket.send(response.encode('utf-8'))

    # Close the client socket
    client_socket.close()


while True:
    # Accept incoming client connections
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    try:
        # Handle the client's request in a separate thread
        handle_request(client_socket)
    except KeyboardInterrupt:
        # Handle Ctrl+C interruption here (if needed)
        pass
