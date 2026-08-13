"""Nodo servidor bancario (Lab 3): escucha en su router gateway y responde
operaciones AUTH/WITHDRAW/ERROR/LOGOUT segun el protocolo acordado.

No confundir con Extras/server.py, que es la demo de capas del Lab 2
(login/withdraw/logout con framing propio) usada como referencia.

Uso: python -m src.endpoints.server <self_id> <gateway_id>
"""
from __future__ import annotations

import argparse
import json
import os
import time

from src.data.banking import handle_incoming
from src.hamming.bits import bits_to_text, text_to_bits
from src.hamming.decode import decode as hamming_decode
from src.hamming.encode import encode as hamming_encode
from src.net.sockets_utils import send_line, start_line_server

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_addressbook() -> dict:
    with open(os.path.join(os.path.dirname(BASE_DIR), "config", "nodos.json")) as f:
        return {k: v for k, v in json.load(f).items() if not k.startswith("_")}


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor bancario de prueba (Lab 3).")
    parser.add_argument("self_id", help="Id de este servidor en config/nodos.json")
    parser.add_argument("gateway_id", help="Id del router gateway en config/nodos.json")
    args = parser.parse_args()

    addressbook = load_addressbook()
    self_addr = addressbook[args.self_id]
    gateway = addressbook[args.gateway_id]

    def on_frame(raw_bits: str, _addr) -> None:
        data_bits = hamming_decode(raw_bits)
        message = json.loads(bits_to_text(data_bits))
        print(f"[{args.self_id}] recibido: {message}")

        response = handle_incoming(message)
        encoded = hamming_encode(text_to_bits(json.dumps(response)))
        send_line(gateway["ip"], gateway["port"], encoded)

    start_line_server(self_addr["ip"], self_addr["port"], on_frame)
    print(f"[{args.self_id}] escuchando en {self_addr['ip']}:{self_addr['port']}")

    while True:
        time.sleep(1)


main()
