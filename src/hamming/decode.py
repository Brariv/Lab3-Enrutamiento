"""Deteccion y correccion de errores Hamming(7,4) (corrige 1 bit erroneo por bloque).

Delega en src/algoritmos/correccionErrores.py (hamming_decodificar), la misma
implementacion generica que usa Extras/capas/enlace.py, aplicada bloque a bloque
de 7 bits para que el resultado sea Hamming(7,4) segun pide el enunciado.
"""

from Extras.algoritmos.correccionErrores import hamming_decodificar


def decode_block(block: str):
    """Devuelve (bloque_recibido, bits_de_datos_corregidos, hubo_error)."""
    if len(block) != 7 or any(b not in "01" for b in block):
        raise ValueError("decode_block espera exactamente 7 bits ('0'/'1')")
    data_bits, hubo_error, _posicion_error = hamming_decodificar(block)
    return block, data_bits, hubo_error


def decode(encoded: str) -> str:
    """Revierte encode(): corrige errores de a un bit por bloque y quita el padding."""
    if len(encoded) < 2:
        raise ValueError("cadena codificada invalida")
    padding = int(encoded[:2], 2)
    payload = encoded[2:]
    if len(payload) % 7 != 0:
        raise ValueError("longitud de payload codificado invalida")
    blocks = [payload[i:i + 7] for i in range(0, len(payload), 7)]
    data = "".join(decode_block(block)[1] for block in blocks)
    if padding:
        data = data[:-padding]
    return data
