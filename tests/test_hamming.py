from src.hamming.decode import decode
from src.hamming.encode import encode


def test_roundtrip_sin_errores():
    original = "1000101111001"
    encoded = encode(original)
    assert decode(encoded) == original


def test_corrige_un_bit_de_error():
    original = "10101010"
    encoded = list(encode(original))
    # Voltea un bit dentro del primer bloque codificado (despues de los 2 bits de padding)
    idx = 5
    encoded[idx] = "1" if encoded[idx] == "0" else "0"
    corrupted = "".join(encoded)
    assert decode(corrupted) == original


def test_texto_a_bits_roundtrip():
    from src.hamming.bits import bits_to_text, text_to_bits

    texto = '{"type": "AUTH"}'
    bits = text_to_bits(texto)
    assert bits_to_text(bits) == texto
