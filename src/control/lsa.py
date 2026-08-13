"""Construccion y flooding de LSAs (Link State Advertisement).

Formato acordado (Lab 3 Protocolo Proposal.pdf):
{
  "type": "LSA", "origin": <id>, "seq": <int>, "ttl": <int>,
  "links": {"<vecino>": <costo>, ...}, "from": <id>
}
"""
from __future__ import annotations

import json
import threading
from typing import Callable, Optional

from src.net.sockets_utils import control_port, send_line


class LSAManager:
    """Guarda el ultimo `seq` visto por origen y reenvia (flood) los LSAs nuevos."""

    def __init__(self, self_id: str, neighbors: dict, addressbook: dict, on_lsa: Optional[Callable[[dict], None]] = None):
        self.self_id = self_id
        self.neighbors = neighbors            # {neighbor_id: costo}
        self.addressbook = addressbook        # {node_id: {"ip":..., "port":...}}
        self.on_lsa = on_lsa                  # callback(lsa) -> usado para alimentar el grafo
        self._last_seq: dict[str, int] = {}
        self._seq_lock = threading.Lock()
        self._own_seq = 0

    def build_own_lsa(self, ttl: int = 16) -> dict:
        with self._seq_lock:
            self._own_seq += 1
            seq = self._own_seq
        return {
            "type": "LSA",
            "origin": self.self_id,
            "seq": seq,
            "ttl": ttl,
            "links": dict(self.neighbors),
            "from": self.self_id,
        }

    def flood_own_lsa(self) -> None:
        lsa = self.build_own_lsa()
        self._remember(lsa["origin"], lsa["seq"])
        self._broadcast(lsa, exclude=None)
        if self.on_lsa:
            self.on_lsa(lsa)

    def handle_incoming(self, lsa: dict) -> None:
        """Procesa un LSA recibido: descarta duplicados/viejos (por seq), reenvia si es nuevo."""
        origin = lsa["origin"]
        seq = lsa["seq"]
        ttl = lsa.get("ttl", 0)

        with self._seq_lock:
            last_seq = self._last_seq.get(origin, -1)
            if seq <= last_seq:
                return  # duplicado o desactualizado -> se descarta (evita loops infinitos)
            self._last_seq[origin] = seq

        if self.on_lsa:
            self.on_lsa(lsa)

        if ttl <= 0:
            return  # limite de propagacion alcanzado

        forwarded = dict(lsa)
        forwarded["ttl"] = ttl - 1
        forwarded["from"] = self.self_id
        self._broadcast(forwarded, exclude=lsa.get("from"))

    def _remember(self, origin: str, seq: int) -> None:
        with self._seq_lock:
            self._last_seq[origin] = seq

    def _broadcast(self, lsa: dict, exclude: Optional[str]) -> None:
        for neighbor_id in self.neighbors:
            if neighbor_id == exclude:
                continue
            addr = self.addressbook.get(neighbor_id)
            if not addr:
                continue
            try:
                send_line(addr["ip"], control_port(addr["port"]), json.dumps(lsa))
            except OSError:
                pass  # vecino caido / no disponible
