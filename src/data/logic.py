"""Capa de red (plano de datos): recibe bits, corrige errores (Hamming 7,4),
consulta nodo_tabla_enrutamiento.csv y reenvia al siguiente salto.

Corresponde a la seccion 3.2 del enunciado. El Hamming(7,4) en si vive en
src/hamming/ (que a su vez reutiliza src/algoritmos/correccionErrores.py).
"""
from __future__ import annotations

import csv
import json
import threading
from typing import Callable, Optional

from src.hamming.bits import bits_to_text, text_to_bits
from src.hamming.decode import decode as hamming_decode
from src.hamming.encode import encode as hamming_encode
from src.net.sockets_utils import send_line, start_line_server


class ForwardingTable:
    """Envuelve nodo_tabla_enrutamiento.csv: destino -> siguiente_salto/ip/puerto."""

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self._table: dict[str, dict] = {}
        self._lock = threading.Lock()
        self.reload()

    def reload(self) -> None:
        table = {}
        try:
            with open(self.csv_path, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    table[row["destino"]] = {
                        "siguiente_salto": row["siguiente_salto"],
                        "ip": row["ip"],
                        "puerto": int(row["puerto"]),
                        "costo": float(row.get("costo", 0)),
                    }
        except FileNotFoundError:
            pass  # aun no se ha calculado la tabla
        with self._lock:
            self._table = table

    def lookup(self, destino: str) -> Optional[dict]:
        with self._lock:
            return self._table.get(destino)


def write_routing_table(csv_path: str, routes: dict, addressbook: dict) -> None:
    """routes: {destino: (costo, siguiente_salto)} -> escribe nodo_tabla_enrutamiento.csv"""
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["destino", "siguiente_salto", "ip", "puerto", "costo"])
        for dest, (costo, next_hop) in routes.items():
            addr = addressbook.get(next_hop, {})
            writer.writerow([dest, next_hop, addr.get("ip", ""), addr.get("port", ""), costo])


class ForwardingLayer:
    """Escucha bits entrantes (post-Hamming), los decodifica y reenvia.

    Un mensaje de datos puede tener como `destination` un router (poco comun
    en Lab 3) o, lo normal, un endpoint (ATM/servidor) que no es router y por
    lo tanto nunca aparece en nodo_tabla_enrutamiento.csv. `endpoints` resuelve
    ese caso: {endpoint_id: id_del_router_gateway}.

    - Si el gateway de ese endpoint soy yo -> lo entrego directo por socket
      (usando `addressbook`, que tiene la ip/puerto real del endpoint).
    - Si el gateway es otro router -> reenvio el mensaje (intacto, con el
      mismo `destination`) hacia ese router usando la tabla de ruteo normal.
    """

    def __init__(
        self,
        self_id: str,
        ip: str,
        port: int,
        table: ForwardingTable,
        addressbook: dict,
        endpoints: Optional[dict] = None,
        on_local_deliver: Optional[Callable[[dict], None]] = None,
    ):
        self.self_id = self_id
        self.ip = ip
        self.port = port
        self.table = table
        self.addressbook = addressbook
        self.endpoints = endpoints or {}
        self.on_local_deliver = on_local_deliver

    def start(self) -> None:
        """Levanta su propio servidor TCP dedicado solo a datos.

        No lo usa src/node.py: ahi HELLO/LSA y datos comparten un unico
        puerto por nodo (asi lo esperan las otras parejas), asi que node.py
        llama directo a `handle_frame()` desde su propio dispatcher. Este
        metodo queda para poder correr/testear ForwardingLayer aislado.
        """
        start_line_server(self.ip, self.port, self.handle_frame)

    def handle_frame(self, raw_bits: str, addr) -> None:
        try:
            data_bits = hamming_decode(raw_bits)
            message = json.loads(bits_to_text(data_bits))
        except (ValueError, UnicodeDecodeError):
            return  # frame corrupto mas alla de lo que Hamming(7,4) puede corregir

        self.forward(message)

    def forward(self, message: dict) -> None:
        destino = message.get("destination")
        gateway_id = self.endpoints.get(destino)

        if gateway_id == self.self_id:
            self._deliver_local(message, destino)
            return

        # Si "destino" es un endpoint con otro gateway, hay que llegar a ese
        # gateway primero; si no es un endpoint conocido, se asume que ya es
        # un id de router y se busca directo en la tabla.
        target = gateway_id or destino

        if target == self.self_id:
            if self.on_local_deliver:
                self.on_local_deliver(message)
            return

        route = self.table.lookup(target)
        if not route:
            return  # sin ruta conocida todavia (o el gateway aun no aparece en el grafo)

        self._send(message, route["ip"], route["puerto"])

    def _deliver_local(self, message: dict, destino: str) -> None:
        addr = self.addressbook.get(destino)
        if not addr:
            return  # el endpoint no tiene ip/puerto registrado en nodos.json
        self._send(message, addr["ip"], addr["port"])
        if self.on_local_deliver:
            self.on_local_deliver(message)

    @staticmethod
    def _send(message: dict, ip: str, port: int) -> None:
        bits = text_to_bits(json.dumps(message))
        encoded = hamming_encode(bits)
        try:
            send_line(ip, port, encoded)
        except OSError:
            pass  # destino/siguiente salto no disponible
