"""Codificacion Hamming(7,4) para el plano de datos (seccion 3.2 del enunciado).

Reutiliza el Hamming generico de src/algoritmos/correccionErrores.py (valido para
cualquier (m, r)) aplicado en bloques fijos de 4 bits de datos, que es exactamente
lo que produce un codeword de 7 bits (m=4 -> r=3 -> n=7). La capa de enlace del
Lab 2 (Extras/capas/enlace.py) usa esa misma funcion para un mensaje completo de
una sola vez; aqui la usamos en bloques para cumplir "Hamming 7,4" bloque a bloque.
"""

from Extras.algoritmos.correccionErrores import hamming_codificar


def encode_block(data_bits: str) -> str:
    """Codifica 4 bits de datos ('0'/'1') en un bloque Hamming(7,4) de 7 bits."""
    if len(data_bits) != 4 or any(b not in "01" for b in data_bits):
        raise ValueError("encode_block espera exactamente 4 bits ('0'/'1')")
    return hamming_codificar(data_bits)


def encode(bits: str) -> str:
    """Codifica una cadena de bits arbitraria.

    Se agregan 2 bits de cabecera (cantidad de padding, 0-3 en binario) seguidos
    de los bloques de 7 bits, para poder reconstruir la longitud original al decodificar.
    """
    if any(b not in "01" for b in bits):
        raise ValueError("encode espera una cadena de '0'/'1'")
    padding = (-len(bits)) % 4
    padded = bits + "0" * padding
    blocks = [padded[i:i + 4] for i in range(0, len(padded), 4)]
    encoded_blocks = "".join(encode_block(block) for block in blocks)
    return f"{padding:02b}" + encoded_blocks
