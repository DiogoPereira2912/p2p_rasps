import socket
import threading

HEADER = 4096
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # get the ip
ADDRESS = (SERVER, PORT)
DISCONNECT_MSG = "DISCONNECT"
MSG_FORMAT = "utf-8"

# create the socket    type of address
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)


def handle_client(conn, addr):
    print(f"New conn {addr}")

    connected = True
    while connected:
        msg = conn.recv(HEADER).decode(MSG_FORMAT)

        if msg == DISCONNECT_MSG:
            connected = False

        print(f"{addr} : {msg}")
        conn.send("MSG RECEIVED".encode(MSG_FORMAT))
    conn.close()


def start():
    server.listen()
    print(f"LISTENING on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"ACTIVE CONNS {threading.active_count() - 1}")


print("SERVER STARTING")
start()