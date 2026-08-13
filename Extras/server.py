import json

from capas import transmision, presentacion, enlace

# Hardcoded "database": card number -> {pin, balance}
ACCOUNTS = {
    "4111111111111111": {"pin": "1234", "balance": 500.00},
    "5500005555555559": {"pin": "0000", "balance": 1200.50},
}

HOST = "127.0.0.1"   # loopback: same machine
PORT = 9001          # arbitrary port above 1024


def enviar_mensaje(conn, obj, algoritmo, bloque=8):
    """Empaqueta un dict de aplicación y lo manda por presentacion -> enlace -> transmision.
    El receptor no aplica ruido (esa capa solo existe del lado del emisor)."""
    texto = json.dumps(obj)
    bits = presentacion.codificar_mensaje(texto)
    trama = enlace.calcular_integridad(bits, algoritmo, bloque)
    transmision.enviar_informacion(conn, trama, algoritmo, bloque)


def recibir_mensaje(lector):
    """Recibe un frame y lo pasa por enlace -> presentacion.
    Returns: (dict | None, algoritmo | None). El dict es None si la conexión
    se cerró o si el mensaje llegó con errores no corregibles."""
    frame = transmision.recibir_informacion(lector)
    if frame is None:
        return None, None

    algoritmo, bloque, trama = frame
    hay_error, bits = enlace.verificar_integridad(trama, algoritmo, bloque)
    corregido = False
    if hay_error:
        bits, corregido = enlace.corregir_mensaje(trama, algoritmo)

    texto = presentacion.decodificar_mensaje(bits, hay_error and not corregido)
    if texto is None:
        return None, algoritmo
    return json.loads(texto), algoritmo


def handle_client(conn):
    authenticated_card = None
    lector = transmision.crear_lector_tramas(conn)

    while True:
        message, algoritmo = recibir_mensaje(lector)
        if message is None:
            print("[SERVER] Client disconnected or unrecoverable message.")
            break

        action = message.get("action")
        data = message.get("data", {})
        print(f"[SERVER] Received: {message}")

        # --- LOGIN ---
        if action == "login":
            card = data.get("card")
            pin = data.get("pin")
            account = ACCOUNTS.get(card)

            if account and account["pin"] == pin:
                authenticated_card = card
                enviar_mensaje(conn, {"action": "login_ok", "data": {"message": "Authentication successful"}}, algoritmo)
            else:
                enviar_mensaje(conn, {"action": "login_denied", "data": {"message": "Invalid card or PIN"}}, algoritmo)

        # --- WITHDRAW ---
        elif action == "withdraw":
            if authenticated_card is None:
                enviar_mensaje(conn, {"action": "error", "data": {"message": "Not authenticated"}}, algoritmo)
                continue

            amount = data.get("amount", 0)
            account = ACCOUNTS[authenticated_card]

            # TODO (students): validate the amount and check for sufficient funds
            # before approving the withdrawal.
            account["balance"] -= amount
            enviar_mensaje(conn, {
                "action": "withdraw_ok",
                "data": {"amount": amount, "balance": account["balance"]},
            }, algoritmo)

        # --- LOGOUT ---
        elif action == "logout":
            enviar_mensaje(conn, {"action": "logout_ok", "data": {"message": "Goodbye"}}, algoritmo)
            print("[SERVER] Client logged out.")
            break

        else:
            enviar_mensaje(conn, {"action": "error", "data": {"message": "Unknown action"}}, algoritmo)


def main():
    server_socket = transmision.crear_socket_servidor(HOST, PORT)
    print(f"[SERVER] Listening on {HOST}:{PORT} ...")

    while True:
        conn, addr = server_socket.accept()
        print(f"[SERVER] Connection from {addr}")
        with conn:
            handle_client(conn)


if __name__ == "__main__":
    main()
