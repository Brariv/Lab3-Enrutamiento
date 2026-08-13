"""Calculo de rutas mas cortas (Dijkstra) sobre el grafo construido con los LSAs."""
from __future__ import annotations

import heapq
from typing import Optional


def shortest_paths(graph: dict, source: str) -> dict:
    """
    graph: {node_id: {neighbor_id: costo}}
    Devuelve {destino: (costo_total, siguiente_salto)} para todo destino alcanzable.
    """
    distances = {source: 0}
    previous: dict[str, str] = {}
    visited = set()
    queue = [(0, source)]

    while queue:
        dist, node = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)

        for neighbor, cost in graph.get(node, {}).items():
            new_dist = dist + cost
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                previous[neighbor] = node
                heapq.heappush(queue, (new_dist, neighbor))

    routes = {}
    for dest, dist in distances.items():
        if dest == source:
            continue
        next_hop = _next_hop(previous, source, dest)
        if next_hop is not None:
            routes[dest] = (dist, next_hop)
    return routes


def _next_hop(previous: dict, source: str, dest: str) -> Optional[str]:
    node = dest
    while previous.get(node) != source:
        node = previous.get(node)
        if node is None:
            return None
    return node
