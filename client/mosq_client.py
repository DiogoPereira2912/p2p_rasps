import socket
import threading
import time
import json
import os

from mqtt_layer import Communication_Layer  


MOSQUITTO_PORT = 1884
BROADCAST_PORT = 50001
BROADCAST_ADDR = "255.255.255.255"
MY_IP = "172.31.1.69" # socket.gethostbyname(socket.gethostname()) -> dá sempre o localhost 
BROKER_ID = MY_IP.replace('.', '_')

# ---- INITIALIZE MQTT CLIENT ----
mqtt_com = Communication_Layer(
    broker=MY_IP,
    port=MOSQUITTO_PORT,
    client_id=f"{BROKER_ID}",
    base_topic="",
    qos=1,
)

mqtt_com.subscribe("#")

# ---- DISCOVERY ----
sock_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_broadcast.bind(("", BROADCAST_PORT))

known_peers = []

# --- PEER DISCOVERY --- #

def add_mosquitto_bridge(peer_ip, peer_port):
    """
        Adiciona uma bridge Mosquitto para um peer recém-descoberto.
        Usa o peer IP como broker_id para o tópico remoto.

        Args:
            peer_ip (str): IP do peer
            peer_port (int): Porta MQTT do peer
    """
    remote_peer_id = peer_ip.replace('.', '_')
    prefix = f"br_{BROKER_ID.split('_')[-1]}/"

    with open(
        "./mosquitto/conf.d/bridges.conf", "r"
    ) as f:  # read the bridges.conf file
        existing_conns = [line.strip() for line in f]

    current_address = f"address {peer_ip}:{peer_port}"

    if any(
        current_address in line for line in existing_conns
    ):  # check if the address has a bridge conn already
        pass
    else:
        bridge_config = f"""
connection bridge_to_peer__{remote_peer_id}
address {peer_ip}:{peer_port}
topic {BROKER_ID}/# out 1 {prefix}
topic {remote_peer_id}/# in 1
            """

        with open("./mosquitto/conf.d/bridges.conf", "a") as f:
            f.write(f"\n{bridge_config}")

        runned = os.system("docker restart mqtt_broker") 
        print(f"Bridge added to {peer_ip}:{peer_port} -> {runned}")
        # time.sleep(10)  # wait for mosquitto to reload config 

def listen_for_peers():
    """
        Thread que escuta mensagens de broadcast para descoberta de peers.
        - Recebe mensagem com porta MQTT
        - Responde para informar qual o seu broker
    """
    while True:
        data, addr = sock_broadcast.recvfrom(1024)
        msg = data.decode()

        if addr[0] == MY_IP:
            continue

        if msg.startswith("hello") or msg.startswith("hi"):
            _, peer_mqtt_port = msg.split()
            peer_mqtt_port = int(peer_mqtt_port)
            peer = (addr[0], peer_mqtt_port)

            if peer not in known_peers:
                known_peers.append(peer)
                print(f"Peers encontrados: {known_peers}")
                for p in known_peers:
                    add_mosquitto_bridge(p[0], p[1])
                    if p != peer:
                        sock_broadcast.sendto(f"hi {peer[1]}".encode(), p)

            if msg.startswith("hello"):
                sock_broadcast.sendto(f"hi {MOSQUITTO_PORT}".encode(), addr)


listener = threading.Thread(target=listen_for_peers, daemon=True)
listener.start()

sock_broadcast.sendto(
    f"hello {MOSQUITTO_PORT}".encode(), (BROADCAST_ADDR, BROADCAST_PORT)
)

# --- MQTT PUB/SUB --- #

def data_publisher():
    ts = 1
    while True:
        time.sleep(3)
        data_sample = {"ts": ts, "msg": f"Cheguei #{ts} de {MY_IP}"}
        try:
            mqtt_com.publish(data_sample, f"{BROKER_ID}/test")
        except Exception as e:
            print(f"Erro ao publicar: {e}")

        print(f"Enviado")
        ts += 1

data_publisher()