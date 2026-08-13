"""Helpers de sockets TCP compartidos por routers, ATM y servidor.

Todo se envia como una linea de texto terminada en '\n':
- Plano de control (HELLO/LSA): la linea es un JSON.
- Plano de datos: la linea es una cadena de bits ('0'/'1') ya codificada con Hamming(7,4).
"""
from __future__ import annotations

import socket
import threading
from typing import Callable, Optional

BUFFER_SIZE = 4096
ENCODING = "utf-8"
CONTROL_PORT_OFFSET = 1000  # puerto de control = puerto de datos + este offset


def control_port(data_port: int) -> int:
    return data_port + CONTROL_PORT_OFFSET


def send_line(ip: str, port: int, text: str, timeout: float = 3.0) -> None:
    """Abre una conexion TCP corta, envia una linea de texto y cierra."""
    data = (text + "\n").encode(ENCODING)
    with socket.create_connection((ip, port), timeout=timeout) as sock:
        sock.sendall(data)


def recv_line(conn: socket.socket) -> Optional[str]:
    """Lee de un socket ya conectado hasta encontrar '\n'."""
    buffer = b""
    while not buffer.endswith(b"\n"):
        chunk = conn.recv(BUFFER_SIZE)
        if not chunk:
            break
        buffer += chunk
    if not buffer:
        return None
    return buffer.decode(ENCODING).strip()


def start_line_server(ip: str, port: int, on_line: Callable[[str, tuple], None], backlog: int = 20) -> socket.socket:
    """Levanta un servidor TCP (en un hilo daemon) que invoca on_line(texto, addr) por conexion."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip, port))
    server.listen(backlog)

    def _serve():
        while True:
            conn, addr = server.accept()
            with conn:
                line = recv_line(conn)
                if line is not None:
                    on_line(line, addr)

    threading.Thread(target=_serve, daemon=True).start()
    return server
