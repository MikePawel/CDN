import socket
import threading
import re

def is_http_request(request):
    pattern = r"^(GET|POST|PUT|DELETE|HEAD)\s+.*\r\n.*"
    match = re.match(pattern, request)
    return match is not None


def handle_request(client_socket, client_address):
    request = client_socket.recv(1024).decode()
    print(f"Received request,{request}")


    #discard request if its not an HTTP request
    if not is_http_request(request):
        return None
    
    server_comsys_socket=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    #Connect to comsys
    server_comsys_socket.connect(("comsys.rwth-aachen.de",80))

    #Forward request to comsys
    server_comsys_socket.sendall(request.encode())

    # Process the HTTP request and generate a response
    response = server_comsys_socket.recv(4096)

    #Send content back to original client
    client_socket.sendall(response)

    #Close both sockets
    server_comsys_socket.close()

    client_socket.close()


def start_server():
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('::', 80))
    server_socket.listen(5)

    print("Server listening on [::]:80")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        thread = threading.Thread(target=handle_request, args=(client_socket, client_address))
        thread.start()

start_server()