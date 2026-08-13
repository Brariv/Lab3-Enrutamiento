import socket
import json

"""
Protocolo de trama compartido con el emisor (JavaScript):
cada envío manda dos líneas de texto terminadas en "\n":
  1) header JSON:  {"algoritmo": "hamming", "bloque": 8, "bits": <n>}
  2) trama de bits: string de '0'/'1' (mensaje + redundancia, + ruido si viene del emisor)
El header va limpio (sin ruido); solo la línea de bits pasa por capas/ruido.py.
"""


def crear_socket_servidor(host, puerto):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, puerto))
    s.listen(1)
    return s


def crear_socket_cliente(host, puerto):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, puerto))
    return s


def crear_lector_tramas(conn):
    """
    Crea un lector de líneas reutilizable sobre la conexión.
    Debe crearse UNA vez por conexión (no en cada recibir_informacion),
    porque internamente usa un buffer con socket.makefile().
    """
    return conn.makefile("r", encoding="utf-8", newline="\n")


def enviar_informacion(conn, trama, algoritmo, bloque=8):
    """
    Args:
        conn: socket conectado/aceptado.
        trama (str): bits ('0'/'1'), con redundancia (y ruido si aplica).
        algoritmo (str): "hamming" | "fletcher" | "crc32".
        bloque (int): tamaño de bloque de fletcher (8/16/32), ignorado si no aplica.
    """
    header = json.dumps({"algoritmo": algoritmo, "bloque": bloque, "bits": len(trama)})
    conn.sendall((header + "\n" + trama + "\n").encode("utf-8"))


def recibir_informacion(lector):
    """
    Bloqueante. Lee un frame completo (header + trama).

    Args:
        lector: objeto devuelto por crear_lector_tramas.
    Returns:
        tuple(str, int, str) | None: (algoritmo, bloque, trama),
        o None si la conexión se cerró.
    """
    linea_header = lector.readline()
    if not linea_header:
        return None
    header = json.loads(linea_header)
    trama = lector.readline().rstrip("\n")
    return header["algoritmo"], header["bloque"], trama
