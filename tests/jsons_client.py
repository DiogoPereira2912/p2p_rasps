import socket
import threading
import time
import json  # <-- para trabalhar com JSON

BROADCAST_PORT = 50001
CHAT_PORT = 50002
BROADCAST_ADDR = "255.255.255.255"
MY_IP = "172.31.1.69"

data_sample = {"ts": 1, "msg": "Cheguei"}

# ---- DISCOVERY ----
sock_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_broadcast.bind(("", BROADCAST_PORT))

known_peers = []


def listen_for_peers():
    while True:
        data, addr = sock_broadcast.recvfrom(1024)
        msg = data.decode()

        if addr[0] == MY_IP:
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

# ---- JSONs Sending ----
sock_chat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_chat.bind(("0.0.0.0", CHAT_PORT))


def chat_listener():
    while True:
        data, _ = sock_chat.recvfrom(1024)
        try:
            decoded = json.loads(data.decode())
            print(f"\r[JSON recebido] ts={decoded['ts']} msg={decoded['msg']}\n> ", end="")
        except json.JSONDecodeError:
            print(f"\r[raw] {data}\n> ", end="")

def json_sender():
    ts = 1
    while True:
        time.sleep(3)  # envia a cada 3 segundos
        data_sample = {"ts": ts, "msg": f"Cheguei #{ts} de {MY_IP}"}
        json_data = json.dumps(data_sample).encode()
        for peer in known_peers:
            sock_chat.sendto(json_data, peer)
        print(f"> Enviado JSON: {data_sample}")
        ts += 1

threading.Thread(target=chat_listener, daemon=True).start()
threading.Thread(target=json_sender, daemon=True).start()

while True:
    time.sleep(1)