import socket

HEADER = 4096
PORT = 5050
SERVER = "127.0.0.1"
DISCONNECT_MSG = "DISCONNECT"
ADDRESS = (SERVER, PORT) 
MSG_FORMAT = "utf-8"


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)

def send(msg):
    message = msg.encode(MSG_FORMAT)
    client.send(message)
    print(client.recv(HEADER).decode(MSG_FORMAT))

send("HELLO WORLD")
input()
send(DISCONNECT_MSG)