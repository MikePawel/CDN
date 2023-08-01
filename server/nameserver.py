from socket import *
from threading import *
from dnslib import *
from random import *

class serverEntry:
    def __init__(self, address, ipArray):
        self.address = address
        self.ipArray = ipArray

entries = [
    serverEntry("comsys.rwth-aachen.DIA-DC.group5.", ["5.200.1.50", "5.200.0.241"]),
    serverEntry("folks.i4.DIA-DC.group5.", ["5.200.1.50", "5.200.0.241"]),
    serverEntry("1.0.0.127.in-addr.arpa.", ["127.0.0.1"])
]

def handle_request(client_data, client_address, server_socket):
    dnsRequest = DNSRecord.parse(client_data)
    response = dnsRequest.reply()

    #Find out which address is being queried
    questionAddress = str(dnsRequest.q.qname).lower()

    #Find out if question is known
    result = [entry for entry in entries if entry.address.lower() == questionAddress]

    #Entry found in database
    if (len(result) > 0):
        #Choose an entry to return. Load balancing depends on how the choice is being made
        print(f"Found entry for {questionAddress}")
        addressToReturn = result[0].ipArray[randint(0, (len(result[0].ipArray) - 1))]
        print(f"Returning {addressToReturn}")

        #Add chosen address to response
        response.add_answer(RR(dnsRequest.q.qname, rdata=A(addressToReturn), ttl=1))

    #Error otherwise    
    else:
        print(f"No entry for {questionAddress}")
        response.header.rcode = RCODE.NXDOMAIN

    #Send content back to original client
    server_socket.sendto(response.pack(), client_address)

def start_server():
    # Set up the server socket
    server_socket = socket.socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 53))
    print("Server listening on localhost:53")

    while True:
        client_data, client_address = server_socket.recvfrom(1024)
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        thread = Thread(target=handle_request, args=(client_data, client_address, server_socket))
        thread.start()

start_server()