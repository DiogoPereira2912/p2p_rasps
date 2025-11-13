import socket
import threading
import time

BROADCAST_PORT = 50001
CHAT_PORT = 50002
BROADCAST_ADDR = "255.255.255.255"
MY_IP = "172.31.1.144"

data_sample = {"ts": 1, "msg": "Cheguei"}

# ---- DISCOVERY ----
sock_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_broadcast.bind(("", BROADCAST_PORT))

# Lista de IPs conhecidos na rede
known_peers = []


def listen_for_peers():
    while True:
        data, addr = sock_broadcast.recvfrom(1024)
        msg = data.decode()

        if addr[0] == MY_IP:  # evitar que conecte a ele próprio
            continue

        if msg.startswith("hello") or msg.startswith("hi"):
            _, peer_chat_port = msg.split()
            peer_chat_port = int(peer_chat_port)
            peer = (addr[0], peer_chat_port)

            if peer not in known_peers:
                known_peers.append(peer)
                print(f"Peers encontrados: {known_peers}")
                for p in known_peers:
                    if p != peer:
                        sock_broadcast.sendto(f"hi {peer[1]}".encode(), p)

            if msg.startswith("hello"):
                sock_broadcast.sendto(f"hi {CHAT_PORT}".encode(), addr)


listener = threading.Thread(target=listen_for_peers, daemon=True)
listener.start()

sock_broadcast.sendto(f"hello {CHAT_PORT}".encode(), (BROADCAST_ADDR, BROADCAST_PORT))

# TODO: substituir com jsons e usar a classe de mqtt
# ---- CHAT ----
sock_chat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_chat.bind(("0.0.0.0", CHAT_PORT))

def chat():
    while True:
        data, _ = sock_chat.recvfrom(1024)
        print("\rpeer: {}\n> ".format(data.decode()), end="")


threading.Thread(target=chat, daemon=True).start()

while True:
    msg = input("> ")
    for peer in known_peers:
        sock_chat.sendto(msg.encode(), peer)
