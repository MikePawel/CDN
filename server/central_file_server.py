import socket
import threading
import re
import random
from datetime import datetime


class Server:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
    def __str__(self):
        return "IP: " + self.ip + " port: " + self.port
  

shared_cache_index={}
pop_servers=[('127.0.0.1',78),('127.0.0.1',79),('127.0.0.1',80),('127.0.0.1',81)]
def header_of_request(request):
    # Split the request by the double CRLF ("\r\n\r\n")
    request_parts = request.split("\r\n\r\n")

    return request_parts[0]


def is_get_request(request):
    pattern = r"^(GET)\s+.*\r\n.*"
    match = re.match(pattern, request)
    return match is not None

#TODO: implement this function
def is_get_request_header(request_header):
    return True

def is_post_request(request):
    pattern = r"^(POST)\s+.*\r\n.*"
    match = re.match(pattern, request)
    return match is not None

def strip_request(request):
    # for now we are only keeping first line, Host and User-Agent
    lines = request.splitlines()

    # Filter and keep desired lines
    desired_lines = [lines[0]]  # Keep the first line by default

    for line in lines:
        if line.startswith(("Host:", "User-Agent:")):
            desired_lines.append(line)
    result = "";
    for d in desired_lines:
        result += f"{d}\r\n"
    result += "\r\n"
    return result


def strip_headers(request):
    # Find the index of the blank line separating headers and body
    blank_line_index = request.find('\r\n\r\n')

    # Extract the request body without the headers
    request_body = request[blank_line_index + 4:]

    return request_body
def choose_server_with(request):
    cache_entry_list = shared_cache_index[request]
    # We can implement a more sophisticated strategy here later
    random_cache_entry = random.choice(cache_entry_list)
    # sender_address is ('127.0.0.1', 80) for e.g.
    if cache_entry_list == []:
        print("Error !")
        return
    return str(random_cache_entry['sender_address'])



def request_server_update(request):

    random_popserver_address = random.choice(pop_servers)

    # remove last two \r\n to add new custom header
    get_request = request[:-2]
    get_request += "Shared-Cache-Lookup: No\r\n\r\n"

    print(f"Now sending the following request to {random_popserver_address} to update cache:")
    print(get_request)

    webserver_socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    webserver_socket.connect(random_popserver_address)

    webserver_socket.sendall(get_request.encode())

    webserver_response = webserver_socket.recv(4096).decode()

    if True:
        print(f"Now {random_popserver_address} has successfuly fetched what we want. Thank you, we'll cache that now")
        return random_popserver_address
    else:
        print(f"Origin fetch of {random_popserver_address} not successful")
        return None


def update_cache(request):
    stripped_request = strip_request(request)
    if stripped_request in shared_cache_index:
        cache_entry_list = shared_cache_index[stripped_request]
    else:
        shared_cache_index[stripped_request] = []
        return
    # assuming latency is very small within a pop, we'll invalidate about the same time the original server invalidates their local cache
    for cache_entry in cache_entry_list:
        if (datetime.now() - cache_entry['creation_time']).total_seconds() > 30:
            # if invalidated remove old entry and create new entry
            print(f"Invalidated this entry now:{cache_entry}")
            cache_entry_list.remove(cache_entry)
            # create new entry by selecting some server to fetch data from origin 
            # we will assume the server does it instantly so we will directly make a new cache entry
            request_server_update(stripped_request)





def handle_get_request(request):
    # update cache and invalidate all entries that are older than 30s
    # for each entry that is invalidated, we will send a request to one of our servers to get us a new entry
    request = strip_request(request)
    update_cache(request)


    if shared_cache_index[request] != []:
        print("Cache hit for:")
        print("Request Header: ")
        print(request)
        return choose_server_with(request)
    else:
        print("Not found in shared cache !")
        print("Request Header: ")
        print(request)
        return "No entry found !"

def get_ip_port(request):
    host_pattern = r"Host:\s+(.+)"
    port_pattern = r"Port:\s+(.+)"
    # Find the Host value using regular expressions
    host_match = re.search(host_pattern, request)
    port_match = re.search(port_pattern,request)

    host_value = host_match.group(1).replace("\r", "").replace("\n", "")
    port_value = int(port_match.group(1).replace("\r", "").replace("\n", ""))
    return (host_value,port_value)


def handle_post_request(request,client_address):
    body = strip_headers(request)

    # The body of a post request should be a get request, that the server is notifying us, he has the data of 
    # so the body of the incoming post request header, is the request the server has the answer to
    # and with the post request he tells us he has it
    if is_get_request_header(body):    

        sender_address = get_ip_port(request)

        # our cache has get requests as keys and a list of dicts as values
        shared_cache_index[body] += [{'sender_address': sender_address, 'creation_time': datetime.now()}]

        print(f"New cache entry in central server:\nKey:\n{body}\nValue:{shared_cache_index[body]}")

        #shared_cache_index[body] = sender_address
        return f"New cache entry in central server:\nKey:\n{body}\nValue:{shared_cache_index[body]}"
    

    else:
        print("Post request received with wrong format")
        print(f"Request:\n{body}")
        return "Cached entry received in wrong format"
    

def create_http_response(message):
    # HTTP response status line
    status_line = "HTTP/1.1 200 OK\r\n"

    # HTTP response headers
    headers = "Content-Type: text/plain\r\n"  # Specify the content type
    headers += "Content-Length: {}\r\n".format(len(message))  # Specify the content length
    headers += "\r\n"  # Empty line to separate headers from the message"

    # Concatenate the status line, headers, and message
    response = status_line + headers + message
    return response
    

# We expect the incoming requests to be already stripped of useless headers
# if not we won't have a cache hit
def handle_connection(client_socket,client_address):
    request = client_socket.recv(4096).decode()
    message = None
    print("Request received: ")
    print(request)
    if is_post_request(request):
        message = handle_post_request(request,client_address)
    if is_get_request(request):
        message = handle_get_request(request)
    
  
    if message == None:
        print("Incoming message stream was not a post or get")
        response = create_http_response("No response sorry")
    else:
        response = create_http_response(message)
    client_socket.sendall(response.encode())
    client_socket.close()

def start_server():
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen(5)

    print("Server listening on localhost:8080")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        if client_address in pop_servers:
            thread = threading.Thread(target=handle_connection, args=(client_socket, client_address))
            thread.start()
        #TODO remove else part to just handle reqeuests from allowed servers
        else:
            thread = threading.Thread(target=handle_connection, args=(client_socket, client_address))
            thread.start()


start_server()