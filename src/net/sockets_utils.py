"""Helpers de sockets TCP compartidos por routers, ATM y servidor.

Todo se envia como una linea de texto terminada en '\n', por un UNICO puerto
por nodo (asi lo esperan las otras 2 parejas de la topologia):
- Plano de control (HELLO/LSA): la linea es un JSON (empieza con '{').
- Plano de datos: la linea es una cadena de bits ('0'/'1') ya codificada con
  Hamming(7,4). src/node.py distingue una de otra mirando el primer caracter.
"""
from __future__ import annotations

import socket
import threading
from typing import Callable, Optional

BUFFER_SIZE = 4096
ENCODING = "utf-8"


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


def recv_lines(conn: socket.socket):
    """Itera TODAS las lineas de una conexion, no solo la primera.

    Las otras parejas no necesariamente abren una conexion nueva por mensaje:
    algunas mantienen la conexion viva y mandan HELLO/LSA/datos seguidos por
    el mismo socket. Leer una sola linea y cerrar hacia que se perdiera todo
    lo que venia despues (por eso este nodo veia los HELLO del vecino pero
    nunca sus LSA, y por lo tanto nunca aprendia la topologia mas alla de sus
    vecinos directos).
    """
    buffer = b""
    while True:
        try:
            chunk = conn.recv(BUFFER_SIZE)
        except (socket.timeout, TimeoutError, OSError):
            break  # peer mudo o caido: se suelta la conexion en vez de bloquear el servidor
        if not chunk:
            break  # el peer cerro
        buffer += chunk
        while b"\n" in buffer:
            raw, buffer = buffer.split(b"\n", 1)
            line = raw.decode(ENCODING, errors="replace").strip()
            if line:
                yield line
    resto = buffer.decode(ENCODING, errors="replace").strip()
    if resto:
        yield resto  # ultima linea sin '\n' final (el peer cerro justo despues)


def start_line_server(
    ip: str,
    port: int,
    on_line: Callable[[str, tuple], None],
    backlog: int = 50,
    conn_timeout: float = 30.0,
) -> socket.socket:
    """Levanta un servidor TCP (en un hilo daemon) que invoca on_line(texto, addr) por cada linea.

    Cada conexion se atiende en su propio hilo: antes se atendian de una en
    una y en el mismo hilo del accept(), asi que un peer que abriera la
    conexion y se quedara callado congelaba TODO el nodo (los mensajes
    siguientes se quedaban encolados sin que nadie los leyera). Ademas
    `on_line` va envuelto en try/except: una excepcion ahi ya no mata el
    servidor completo.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip, port))
    server.listen(backlog)

    def _handle(conn: socket.socket, addr) -> None:
        with conn:
            conn.settimeout(conn_timeout)
            for line in recv_lines(conn):
                try:
                    on_line(line, addr)
                except Exception as exc:  # noqa: BLE001 - un mensaje malo no debe tumbar el nodo
                    print(f"[sockets] error procesando linea de {addr}: {exc!r}", flush=True)

    def _serve():
        while True:
            try:
                conn, addr = server.accept()
            except OSError:
                break  # socket cerrado
            threading.Thread(target=_handle, args=(conn, addr), daemon=True).start()

    threading.Thread(target=_serve, daemon=True).start()
    return server
