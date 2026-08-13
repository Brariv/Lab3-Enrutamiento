from Extras.algoritmos import correccionErrores as correccion
from Extras.algoritmos import deteccionErrores as deteccion


def calcular_integridad(trama, algoritmo, bloque=8):
    """
    Args:
        trama (str): bits del mensaje (salida de presentacion.codificar_mensaje).
        algoritmo (str): "hamming" | "fletcher" | "crc32".
        bloque (int): solo aplica a fletcher (8, 16 o 32).
    Returns:
        str: trama original + bits de redundancia concatenados.
    """
    if algoritmo == "hamming":
        return correccion.hamming_codificar(trama)
    if algoritmo == "fletcher":
        return trama + deteccion.fletcher_calcular(trama, bloque)
    if algoritmo == "crc32":
        return trama + deteccion.crc32_calcular(trama)
    raise ValueError(f"Algoritmo desconocido: {algoritmo}")


def verificar_integridad(trama_recibida, algoritmo, bloque=8):
    """
    Args:
        trama_recibida (str): bits + redundancia, tal como llegó por la red.
    Returns:
        tuple(bool, str): (hay_error, trama_sin_redundancia).
    """
    if algoritmo == "hamming":
        mensaje, hay_error, _ = correccion.hamming_decodificar(trama_recibida)
        return hay_error, mensaje
    if algoritmo == "fletcher":
        ok = deteccion.fletcher_verificar(trama_recibida, bloque)
        return (not ok), trama_recibida[:-2 * bloque]
    if algoritmo == "crc32":
        ok = deteccion.crc32_verificar(trama_recibida)
        return (not ok), trama_recibida[:-32]
    raise ValueError(f"Algoritmo desconocido: {algoritmo}")


def corregir_mensaje(trama_recibida, algoritmo):
    """
    Solo tiene efecto real con "hamming" (fletcher/crc32 solo detectan).
    Returns:
        tuple(str, bool): (trama_corregida, se_pudo_corregir).
    """
    if algoritmo == "hamming":
        mensaje, hay_error, _ = correccion.hamming_decodificar(trama_recibida)
        return mensaje, hay_error
    return trama_recibida, False
