"""Descubrimiento de vecinos vivos vía paquetes HELLO periodicos."""
from __future__ import annotations

import json
import threading
import time
from typing import Callable, Optional

from src.net.sockets_utils import control_port, send_line


class HelloManager:
    def __init__(
        self,
        self_id: str,
        neighbors: dict,
        addressbook: dict,
        interval: float = 2.0,
        timeout: float = 6.0,
        on_link_change: Optional[Callable[[str, bool], None]] = None,
    ):
        self.self_id = self_id
        self.neighbors = neighbors
        self.addressbook = addressbook
        self.interval = interval
        self.timeout = timeout
        self.on_link_change = on_link_change
        self._last_seen = {n: 0.0 for n in neighbors}
        self._up = {n: False for n in neighbors}
        self._lock = threading.Lock()

    def start(self) -> None:
        threading.Thread(target=self._send_loop, daemon=True).start()
        threading.Thread(target=self._check_loop, daemon=True).start()

    def handle_hello(self, message: dict) -> None:
        sender = message.get("from")
        if sender not in self.neighbors:
            return
        with self._lock:
            self._last_seen[sender] = time.time()
            if not self._up.get(sender, False):
                self._up[sender] = True
                if self.on_link_change:
                    self.on_link_change(sender, True)

    def _send_loop(self) -> None:
        while True:
            hello = {"type": "HELLO", "from": self.self_id}
            for neighbor_id in self.neighbors:
                addr = self.addressbook.get(neighbor_id)
                if not addr:
                    continue
                try:
                    send_line(addr["ip"], control_port(addr["port"]), json.dumps(hello))
                except OSError:
                    pass
            time.sleep(self.interval)

    def _check_loop(self) -> None:
        while True:
            time.sleep(self.interval)
            now = time.time()
            with self._lock:
                for neighbor_id, last_seen in self._last_seen.items():
                    if self._up.get(neighbor_id) and last_seen and now - last_seen > self.timeout:
                        self._up[neighbor_id] = False
                        if self.on_link_change:
                            self.on_link_change(neighbor_id, False)
