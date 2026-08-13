"""Serializacion/deserializacion de mensajes de datos segun el protocolo acordado.

{ "type": ..., "origin": <ip_nodo_ATM>, "destination": <ip_nodo_servidor>, "payload": {...} }
"""
import json


def build_data_message(msg_type: str, origin: str, destination: str, payload: dict) -> dict:
    """msg_type: 'AUTH' | 'WITHDRAW' | 'ERROR' | 'LOGOUT'."""
    return {
        "type": msg_type,
        "origin": origin,
        "destination": destination,
        "payload": payload,
    }


def to_json(message: dict) -> str:
    return json.dumps(message)


def from_json(raw: str) -> dict:
    return json.loads(raw)
