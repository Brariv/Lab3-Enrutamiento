"""
Fletcher checksum (o CRC-32 como alternativa). Implementar (algoritmo de
detección asignado a otro integrante del equipo).
"""


def fletcher_calcular(datos, bloque):
    """
    Args:
        datos (str): bits del mensaje.
        bloque (int): 8, 16 o 32 (configurable); aplicar padding de ceros
                      si datos no es múltiplo del bloque.
    Returns:
        str: bits del checksum (2 * bloque bits: suma A + suma B).
    """
    if bloque not in (8, 16, 32):
        raise ValueError("bloque debe ser 8, 16 o 32")

    # pad datos to multiple of bloque
    pad = (-len(datos)) % bloque
    if pad:
        datos = datos + '0' * pad

    mod = 1 << bloque
    suma_a = 0
    suma_b = 0
    for i in range(0, len(datos), bloque):
        palabra = int(datos[i:i + bloque], 2)
        suma_a = (suma_a + palabra) % mod
        suma_b = (suma_b + suma_a) % mod

    return format(suma_a, '0{}b'.format(bloque)) + format(suma_b, '0{}b'.format(bloque))


def fletcher_verificar(datos_con_checksum, bloque):
    """
    Returns:
        bool: True si no hay error detectado.
    """
    total_len = len(datos_con_checksum)
    if total_len < 2 * bloque:
        return False

    datos = datos_con_checksum[: total_len - 2 * bloque]
    checksum_recibido = datos_con_checksum[total_len - 2 * bloque:]
    checksum_calculado = fletcher_calcular(datos, bloque)
    return checksum_calculado == checksum_recibido


# --- Alternativa: CRC-32 ---

def crc32_calcular(datos, polinomio=0x04C11DB7):
    """
    Args:
        datos (str): bits del mensaje (n > 32, o padding si es menor).
        polinomio (int): estándar CRC-32 (32 bits).
    Returns:
        str: 32 bits de residuo (CRC) a concatenar.
    """
    # Convert polynomial to include implicit leading 1 at bit 32
    poly = polinomio | (1 << 32)

    data_len = len(datos)
    data_int = int(datos, 2) if datos else 0

    # append 32 zeros
    remainder = data_int << 32

    for shift in range(data_len + 32 - 1, 31, -1):
        if remainder & (1 << shift):
            remainder ^= (poly << (shift - 32))

    crc = remainder & ((1 << 32) - 1)
    return format(crc, '032b')


def crc32_verificar(datos_con_crc, polinomio=0x04C11DB7):
    """
    Returns:
        bool: True si el residuo calculado da 0 (sin error).
    """
    poly = polinomio | (1 << 32)

    total_len = len(datos_con_crc)
    if total_len < 32:
        return False

    remainder = int(datos_con_crc, 2)

    for shift in range(total_len - 1, 31, -1):
        if remainder & (1 << shift):
            remainder ^= (poly << (shift - 32))

    return (remainder & ((1 << 32) - 1)) == 0
