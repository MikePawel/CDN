import socket
import threading
import re

cache={}

# TODO: do we cache  just based on the HTTP Request GET /team HTTP/1.1 or do we take headers into account too ?


def is_http_request(request):
    pattern = r"^(GET|POST|PUT|DELETE|HEAD)\s+.*\r\n.*"
    match = re.match(pattern, request)
    return match is not None


def handle_request(client_socket, client_address):
    request = client_socket.recv(1024).decode()
    #TODO: Request muss noch überarbeitet werden, nur die nötigen Teile vom request benutzen und cachen
    #discard request if its not an HTTP request
    if not is_http_request(request):
        return None
    
    if request in cache:
        print(f"Cache hit for request: {request}")
        response = cache[request]
        print(response)
    else:
        print(f"Cache Miss for request: {request}")
        server_comsys_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Connect to comsys
        server_comsys_socket.connect(("www.comsys.rwth-aachen.de",80))

        #Forward request to comsys
        server_comsys_socket.sendall(request.encode())
        # Process the HTTP request and generate a response
        response = server_comsys_socket.recv(4096)
        print(response)
    
        #Cache the response
        cache[request] = response
    

        #Send content back to original client
        client_socket.sendall(response)

        #Close both sockets
        server_comsys_socket.close()

    client_socket.close()


def start_server():
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(5)

    print("Server listening on [::]:80")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        thread = threading.Thread(target=handle_request, args=(client_socket, client_address))
        thread.start()

start_server()