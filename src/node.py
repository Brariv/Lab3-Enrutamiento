"""Entry point de un nodo router: arranca HELLO, LSA, calculo de rutas y forwarding en paralelo.

Uso: python -m src.node <node_id>
"""
from __future__ import annotations

import argparse
import json
import os
import threading
import time

LSA_REFRESH_INTERVAL = 15.0  # segundos entre re-floods periodicos, aunque nada haya cambiado

from src.control.dijkstra import shortest_paths
from src.control.graph import NetworkGraph
from src.control.hello import HelloManager
from src.control.lsa import LSAManager
from src.data.logic import ForwardingLayer, ForwardingTable, write_routing_table
from src.net.sockets_utils import start_line_server

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config(node_id: str):
    with open(os.path.join(BASE_DIR, "config", "nodos.json")) as f:
        addressbook = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
    with open(os.path.join(BASE_DIR, "config", "topologia.json")) as f:
        topologia = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
    endpoints_path = os.path.join(BASE_DIR, "config", "endpoints.json")
    endpoints = {}
    if os.path.exists(endpoints_path):
        with open(endpoints_path) as f:
            endpoints = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
    return addressbook, topologia.get(node_id, {}), endpoints


def main() -> None:
    parser = argparse.ArgumentParser(description="Levanta un nodo router del Lab 3.")
    parser.add_argument("node_id", help="Identificador del nodo (debe existir en config/nodos.json)")
    args = parser.parse_args()

    node_id = args.node_id
    addressbook, neighbors, endpoints = load_config(node_id)
    if node_id not in addressbook:
        raise SystemExit(f"'{node_id}' no existe en config/nodos.json")
    self_addr = addressbook[node_id]
    csv_path = os.path.join(BASE_DIR, "data", f"nodo_{node_id}_tabla_enrutamiento.csv")

    graph = NetworkGraph()
    table = ForwardingTable(csv_path)

    graph.update_from_lsa({"origin": node_id, "links": neighbors})  # se conoce a si mismo desde el inicio

    def recompute_routes() -> None:
        snapshot = graph.snapshot()
        routes = shortest_paths(snapshot, node_id)
        write_routing_table(csv_path, routes, addressbook)
        table.reload()
        print(f"[{node_id}] tabla actualizada: {routes}", flush=True)

    def on_lsa_learned(lsa: dict) -> None:
        # Aca es donde se aprende la topologia del resto de la red: cada LSA nuevo
        # (propio o ajeno) aporta las adyacencias de su "origin" al grafo local.
        graph.update_from_lsa(lsa)
        recompute_routes()

    lsa_manager = LSAManager(node_id, neighbors, addressbook, on_lsa=on_lsa_learned)

    def on_link_change(neighbor_id: str, is_up: bool) -> None:
        estado = "UP" if is_up else "DOWN"
        print(f"[{node_id}] enlace con {neighbor_id}: {estado}", flush=True)
        if is_up:
            lsa_manager.flood_own_lsa()
        # TODO: si el enlace cae, quitarlo del grafo/topologia y recalcular rutas.

    hello_manager = HelloManager(node_id, neighbors, addressbook, on_link_change=on_link_change)

    def on_local_deliver(message: dict) -> None:
        print(f"[{node_id}] mensaje entregado localmente a {message.get('destination')}: {message}", flush=True)

    forwarding = ForwardingLayer(
        node_id,
        self_addr["ip"],
        self_addr["port"],
        table,
        addressbook,
        endpoints,
        on_local_deliver,
        # Se relee en cada frame: cambiar endpoints.json ya no obliga a reiniciar el nodo.
        endpoints_path=os.path.join(BASE_DIR, "config", "endpoints.json"),
    )
    print(f"[{node_id}] endpoints locales: {endpoints}", flush=True)

    def on_incoming_line(raw_line: str, _addr) -> None:
        # Un solo puerto para todo (asi lo esperan las otras parejas): un
        # frame de datos ya paso por Hamming(7,4), asi que solo tiene '0'/'1';
        # un mensaje de control (HELLO/LSA) siempre es JSON y empieza con '{'.
        if raw_line and raw_line[0] in "01":
            forwarding.handle_frame(raw_line, _addr)
            return

        try:
            message = json.loads(raw_line)
        except ValueError:
            print(f"[{node_id}] linea ignorada (ni bits ni JSON): {raw_line[:80]!r}", flush=True)
            return  # linea corrupta/mal formada: se descarta sin tumbar el hilo del servidor

        tipo = message.get("type")
        if tipo == "HELLO":
            hello_manager.handle_hello(message)
        elif tipo == "LSA":
            lsa_manager.handle_incoming(message)
        else:
            print(f"[{node_id}] mensaje de control desconocido (type={tipo!r}): {raw_line[:120]}", flush=True)

    start_line_server(self_addr["ip"], self_addr["port"], on_incoming_line)
    hello_manager.start()

    def _lsa_refresh_loop() -> None:
        # Re-manda el LSA propio cada rato, no solo cuando un enlace cambia de
        # estado. Esto arregla el caso en que un vecino no estaba escuchando
        # todavia cuando se mando el primer flood al arrancar (send_line
        # falla en silencio con ConnectionRefused y nadie lo reintentaba), o
        # cuando un nodo se reinicia y su vecino nunca detecto el enlace caido
        # (timeout de HELLO de 6s) para volver a re-floodear hacia el.
        while True:
            time.sleep(LSA_REFRESH_INTERVAL)
            lsa_manager.flood_own_lsa()

    threading.Thread(target=_lsa_refresh_loop, daemon=True).start()

    recompute_routes()
    lsa_manager.flood_own_lsa()

    print(
        f"[{node_id}] escuchando en {self_addr['ip']}:{self_addr['port']} (control + datos)",
        flush=True,
    )

    while True:
        time.sleep(1)


main()
