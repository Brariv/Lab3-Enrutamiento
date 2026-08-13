from src.control.dijkstra import shortest_paths


def test_ruta_mas_corta_simple():
    graph = {
        "A": {"B": 2, "C": 5},
        "B": {"A": 2, "C": 1},
        "C": {"A": 5, "B": 1},
    }
    routes = shortest_paths(graph, "A")
    assert routes["B"] == (2, "B")
    assert routes["C"] == (3, "B")  # A->B->C (3) es mas barato que A->C directo (5)


def test_nodo_inalcanzable_no_aparece():
    graph = {
        "A": {"B": 1},
        "B": {"A": 1},
        "C": {},  # aislado
    }
    routes = shortest_paths(graph, "A")
    assert "C" not in routes
