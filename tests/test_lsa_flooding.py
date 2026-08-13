from src.control.lsa import LSAManager


def test_descarta_lsa_con_seq_menor_o_igual():
    received = []
    manager = LSAManager("A", neighbors={"B": 1}, addressbook={}, on_lsa=received.append)

    lsa_1 = {"type": "LSA", "origin": "X", "seq": 5, "ttl": 3, "links": {}, "from": "B"}
    lsa_2_duplicado = {"type": "LSA", "origin": "X", "seq": 5, "ttl": 3, "links": {}, "from": "B"}
    lsa_3_nuevo = {"type": "LSA", "origin": "X", "seq": 6, "ttl": 3, "links": {}, "from": "B"}

    manager.handle_incoming(lsa_1)
    manager.handle_incoming(lsa_2_duplicado)
    manager.handle_incoming(lsa_3_nuevo)

    assert len(received) == 2  # el duplicado (seq igual) se descarta


def test_ttl_cero_no_se_reenvia_pero_si_se_aprende():
    received = []
    manager = LSAManager("A", neighbors={"B": 1}, addressbook={}, on_lsa=received.append)

    lsa = {"type": "LSA", "origin": "X", "seq": 1, "ttl": 0, "links": {"Y": 2}, "from": "B"}
    manager.handle_incoming(lsa)

    assert len(received) == 1
    assert received[0]["links"] == {"Y": 2}
