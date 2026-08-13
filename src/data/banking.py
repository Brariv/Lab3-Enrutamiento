"""Payloads de operaciones bancarias (ATM <-> Servidor) y logica de sesion del lado servidor.

`auth`, `withdraw`, `logout` y `error` solo arman el JSON del mensaje (las usa
tanto el cliente para pedir, como el servidor para responder con el mismo
`type`). La validacion contra data/banking_data.json y el seguimiento de
sesion (para no pedir PIN en cada retiro) vive en `handle_incoming`, que es
lo que llama src/endpoints/server.py por cada frame que le llega.

Nota: el payload de WITHDRAW usa la clave "user" (no "cuenta" como decia
Lab 3 Protocolo Proposal.pdf) para reusar el mismo nombre que AUTH. Si las
otras 2 parejas ya esperan "cuenta", hay que acordarlo y ajustar aqui.
"""
from __future__ import annotations

import json
import os

from src.data.messages import build_data_message

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_BANKING_DATA_PATH = os.path.join(BASE_DIR, "data", "banking_data.json")

with open(_BANKING_DATA_PATH, "r") as _f:
    _BANKING_DATA = json.load(_f)

# bank_name -> {nombre_cuenta: cuenta_dict}, se arma la primera vez que se pide.
_ACCOUNTS_CACHE: dict = {}

# client_id (id del ATM) -> nombre de la cuenta con sesion activa en ese banco
_SESSIONS: dict = {}


def auth(origin: str, destination: str, user: str, pin: str) -> dict:
    return build_data_message("AUTH", origin, destination, {"user": user, "pin": pin})


def withdraw(origin: str, destination: str, user: str, monto: float) -> dict:
    return build_data_message("WITHDRAW", origin, destination, {"user": user, "monto": monto})


def error(origin: str, destination: str, code: str, detalle: str) -> dict:
    return build_data_message("ERROR", origin, destination, {"code": code, "detalle": detalle})


def logout(origin: str, destination: str) -> dict:
    return build_data_message("LOGOUT", origin, destination, {})


def _accounts_for(bank_name: str) -> dict:
    if bank_name not in _ACCOUNTS_CACHE:
        cuentas = _BANKING_DATA.get(bank_name, {}).get("Cuentas", [])
        _ACCOUNTS_CACHE[bank_name] = {cuenta["nombre"]: cuenta for cuenta in cuentas}
    return _ACCOUNTS_CACHE[bank_name]


def handle_incoming(message: dict) -> dict:
    """Logica del lado servidor: valida contra banking_data.json, mantiene la
    sesion del cliente e imprime cada inicio de sesion, retiro y logout."""
    msg_type = message.get("type")
    client_id = message.get("origin")        # id del ATM que mando la solicitud
    bank_name = message.get("destination")   # id de este banco, tal como lo vio el cliente
    origin = bank_name                        # el servidor responde desde donde le llego
    destination = client_id
    payload = message.get("payload") or {}

    if msg_type == "AUTH":
        user = payload.get("user")
        pin = payload.get("pin")
        cuenta = _accounts_for(bank_name).get(user)

        if cuenta is not None and cuenta["pin"] == pin:
            _SESSIONS[client_id] = user
            print(f"[{bank_name}] LOGIN OK -> {client_id} (usuario={user}, saldo={cuenta['saldo']})", flush=True)
            return build_data_message("AUTH", origin, destination, {"status": "ok", "saldo": cuenta["saldo"]})

        print(f"[{bank_name}] LOGIN DENEGADO -> {client_id} (usuario={user})", flush=True)
        return build_data_message("AUTH", origin, destination, {"status": "denied", "message": "usuario o PIN invalido"})

    if msg_type == "WITHDRAW":
        user = _SESSIONS.get(client_id)
        if not user:
            print(f"[{bank_name}] RETIRO rechazado -> {client_id}: sin sesion activa", flush=True)
            return error(origin, destination, "NOT_AUTHENTICATED", "inicia sesion antes de retirar")

        monto = payload.get("monto")
        cuenta = _accounts_for(bank_name)[user]

        if not isinstance(monto, (int, float)) or monto <= 0 or monto > cuenta["saldo"]:
            print(f"[{bank_name}] RETIRO RECHAZADO -> {client_id} (usuario={user}, monto={monto}, saldo={cuenta['saldo']})", flush=True)
            return build_data_message(
                "WITHDRAW",
                origin,
                destination,
                {"status": "error", "message": "monto invalido o saldo insuficiente", "saldo": cuenta["saldo"]},
            )

        cuenta["saldo"] -= monto
        print(f"[{bank_name}] RETIRO OK -> {client_id} (usuario={user}, monto={monto}, nuevo saldo={cuenta['saldo']})", flush=True)
        return build_data_message("WITHDRAW", origin, destination, {"status": "ok", "saldo": cuenta["saldo"]})

    if msg_type == "LOGOUT":
        user = _SESSIONS.pop(client_id, None)
        print(f"[{bank_name}] LOGOUT -> {client_id} (usuario={user})", flush=True)
        return build_data_message("LOGOUT", origin, destination, {"status": "ok"})

    return error(origin, destination, "UNKNOWN_TYPE", f"tipo no soportado: {msg_type}")
