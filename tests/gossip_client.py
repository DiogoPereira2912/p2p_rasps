import socket
import threading
import time
import random
import pickle  # para serializar a lista de peers

BROADCAST_PORT = 50001
CHAT_PORT = 50002
BROADCAST_ADDR = "255.255.255.255"

# Descobre o IP local automaticamente
MY_IP = "172.31.1.206"

# Lista de peers conhecidos
known_peers = []

# ---- SOCKETS ----
sock_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_broadcast.bind(("", BROADCAST_PORT))

sock_chat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_chat.bind(("0.0.0.0", CHAT_PORT))

def serialize(peers):
    return pickle.dumps(peers)

def deserialize(data):
    return pickle.loads(data)

def chat():
    while True:
        data, _ = sock_chat.recvfrom(1024)
        print("\rpeer: {}\n> ".format(data.decode()), end="")

# Recebe listas de peers via Gossip
def gossip_listener():
    while True:
        data, addr = sock_broadcast.recvfrom(4096)
        try:
            received_list = deserialize(data)
        except:
            continue  # ignora pacotes inválidos
        updated = False
        for peer in received_list:
            if peer not in known_peers and peer[0] != MY_IP:
                known_peers.append(peer)
                updated = True
        if updated:
            print(f"Lista de peers atualizada: {known_peers}")

def gossip_sender():
    while True:
        time.sleep(0.1)
        if known_peers:
            peer = random.choice(known_peers)
            sock_broadcast.sendto(serialize(known_peers), (peer[0], BROADCAST_PORT))

# ---- THREADS ----
threading.Thread(target=gossip_listener, daemon=True).start()
threading.Thread(target=gossip_sender, daemon=True).start()
threading.Thread(target=chat, daemon=True).start()

# ---- BROADCAST INICIAL ----
sock_broadcast.sendto(serialize([(MY_IP, CHAT_PORT)]), (BROADCAST_ADDR, BROADCAST_PORT))
print("Broadcast inicial enviado. Agora podes enviar mensagens!\n")

# ---- CHAT LOOP ----
while True:
    msg = input('> ')
    for peer in known_peers:
        sock_chat.sendto(msg.encode(), peer)
