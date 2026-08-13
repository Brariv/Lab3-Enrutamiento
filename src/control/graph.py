"""Construccion del grafo de la red a partir de los LSAs recibidos."""
from __future__ import annotations

import threading


class NetworkGraph:
    def __init__(self):
        self._links: dict[str, dict[str, float]] = {}
        self._lock = threading.Lock()

    def update_from_lsa(self, lsa: dict) -> None:
        origin = lsa["origin"]
        links = lsa.get("links", {})
        with self._lock:
            self._links[origin] = dict(links)

    def snapshot(self) -> dict:
        with self._lock:
            return {node: dict(neighbors) for node, neighbors in self._links.items()}
