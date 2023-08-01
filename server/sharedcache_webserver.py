import socket
import sys
import threading
import re
from datetime import datetime



class UrlEntry:
    def __init__(self, addressLocal, addressGlobal):
        self.addressLocal = addressLocal
        self.addressGlobal = addressGlobal

args = sys.argv[1:]
(central_server_ip,central_server_port) = ("127.0.0.1", 8080)
cache={}
entries = [
    UrlEntry("comsys.rwth-aachen.DIA-DC.group5", "comsys.rwth-aachen.de"),
    UrlEntry("folks.i4.DIA-DC.group5", "folks.i4.de"),
]
own_ip_address="127.0.0.1"
port = int(args[0])
# id to idenfify a server within a pop
# for now for local testing we we will use port 
pop_id = port




def is_http_request(request):
    pattern = r"^(GET|POST|PUT|DELETE|HEAD)\s+.*\r\n.*"
    match = re.match(pattern, request)
    return match is not None

def update_cache(changed_request):
        if changed_request in cache and (datetime.now() - cache[changed_request]['creation_time']).total_seconds() > 30 :
            cache.pop(changed_request)

def strip_headers(request):
    # Find the index of the blank line separating headers and body
    blank_line_index = request.find('\r\n\r\n')

    # Extract the request body without the headers
    request_body = request[blank_line_index + 4:]

    return request_body

def extract_client_address_from_response(response):
    response = strip_headers(response)
    clean_string = response.strip('()')
    

    # Splitting the string by comma and removing any whitespace
    values = [value.strip() for value in clean_string.split(',')]

    # Extracting the two values
    ip_address = values[0].strip("'")
    port = int(values[1])
    return (ip_address,port)

def create_http_post_request(message):
    request = f"POST / HTTP/1.1\r\n"
    request += f"Host: {own_ip_address}\r\n"
    request += f"Port: {port}\r\n"
    request += "Content-Type: text/plain\r\n"
    request += f"Content-Length: {len(message)}\r\n"
    request += "\r\n"
    request += message
    return request


def notify_central_server(changed_request):
    # The central server caches only post requests
    # Create HTTP post request with the body being the changed_request
    print("Now notifying central server of the entry now cached at this server")
    central_server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    central_server_socket.connect((central_server_ip,central_server_port))

    http_post_request = create_http_post_request(changed_request)
    # Send encoded HTTP post request
    central_server_socket.sendall(http_post_request.encode())

    central_server_response = central_server_socket.recv(4096).decode()

    if "New cache entry" in central_server_response:
        print("Central server notified successfully.")
    else:
        print("Notfication not succesful.")

    central_server_socket.close()




def shared_cache_lookup(changed_request):
    #TODO add hashes
    # Create socket to connect to central server, that has 
    central_server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    central_server_socket.connect((central_server_ip,central_server_port))
    central_server_socket.sendall(changed_request.encode())
    # response will look like this ('127.0.0.1', 54876) if the shared cache found something
    #else response is "No Entry Found"
    central_server_response = central_server_socket.recv(4096).decode()
    print("Central server responded to shared cache lookup with:")
    print(central_server_response)
    if "No entry found !" in central_server_response:
        central_server_socket.close()
        return None
    
    central_server_socket.close()
    return extract_client_address_from_response(central_server_response)

def change_host_header(request):
    changed_request = request
    hostvalue = host_value(request)
    result = [entry for entry in entries if entry.addressLocal.lower() == hostvalue]
    if result == []:
        return None
    changed_request = re.sub(r"(?<=Host: )[^ \r\n]+", result[0].addressGlobal, changed_request)
    return changed_request

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

def modify_request_for_central_server(request):
    #strip request of headers we don't want first
    request = strip_request(request)
    # Add pop-server identification header
    # First Remove the last \r\n\r\n
    request += f"POP-ID: {pop_id}\r\n\r\n"

    return request



# Shared lookup is allowed, if the request does not contain the header Shared-Cache-Lookup: No
# this we need if we get the order from the central server to go fetch something from origin
# in that case it wouldn't make sense to go ask the central server, because he'd only tell us to fetch something if he does not have it
def shared_lookup_allowed(request):
    return not "Shared-Cache-Lookup: No" in request

def host_value(request):
    pattern = re.findall(r"(?<=Host:) .*(?=\r)", request)[0]
    hostHeader = re.sub('\s', '', pattern)
    return hostHeader

def handle_request(client_socket,client_address):
    request = client_socket.recv(1024).decode()
    print(f"Request:\n {request}")
    #discard request if its not an HTTP request
    if not is_http_request(request):
        print("Not an http request !")
        return None   
    changed_request = change_host_header(request)

    if changed_request is None:
        print("Sorry, you are trying to access a website we are not hosting.")
        return     

    stripped_request = strip_request(request)

    #Check the age of the request stored in the cache and remove it if its over 30s old.
    update_cache(stripped_request)


    if stripped_request in cache:
            # Result was directly found locally
            print(f"Local cache hit for request: {stripped_request}")
            response = cache[stripped_request]['response']
    else:
        # Check shared cache first
        if shared_lookup_allowed(request):
            shared_cache_response = shared_cache_lookup(modify_request_for_central_server(request))
            if shared_cache_response != None and (shared_cache_response[1] != port or shared_cache_response[0] != own_ip_address):
                print(f"Shared Cache hit\nNow contacting: {shared_cache_response}")
                (server_ip,server_port) = shared_cache_response
            else:
                print("Now contacting origin")
                server_ip = host_value(changed_request) 
                server_port = 80
        else:
            print("Now contacting origin")
            server_ip = host_value(changed_request) 
            server_port = 80
            
        socket_to_fileserver=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        #Connect to original website
        socket_to_fileserver.connect((server_ip,server_port))

        #Forward request
        socket_to_fileserver.sendall(changed_request.encode())
        
        # Process the HTTP request and generate a response
        response = socket_to_fileserver.recv(4096)

        #Cache the response
        cache[stripped_request] = {'response': response, 'creation_time': datetime.now()}

        #Tell shared cache central server we now have the response "response" cached locally
        notify_central_server(stripped_request)
    
        #Close socket to origin
        socket_to_fileserver.close()

          
      

    #Send content back to original client and close socket
    client_socket.sendall(response)
    client_socket.close()


def start_server():
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)


    print(f"Server listening on localhost:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        thread = threading.Thread(target=handle_request, args=(client_socket, client_address))
        thread.start()

start_server()
