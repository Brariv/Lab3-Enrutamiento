"""
Código de Hamming. Implementar (algoritmo de corrección asignado a un
integrante del equipo). Debe ser válido para cualquier (n, m) que cumpla
m + r + 1 <= 2^r.
"""


def hamming_calcular_r(m):
    """
    Args:
        m (int): bits de datos.
    Returns:
        int: menor r tal que m + r + 1 <= 2^r.
    """
    r = 0
    while m + r + 1 > (1 << r):
        r += 1
    return r


def hamming_codificar(bits):
    """
    Inserta bits de paridad en las posiciones potencia de 2.

    Args:
        bits (str): mensaje de m bits.
    Returns:
        str: palabra código completa (codeword).
    """
    m = len(bits)
    r = hamming_calcular_r(m)
    n = m + r

    # Build codeword with placeholders for parity bits (positions 1,2,4,...)
    code = []
    data_index = 0
    for i in range(1, n + 1):
        # if i is power of two -> parity bit
        if (i & (i - 1)) == 0:
            code.append('0')
        else:
            code.append(bits[data_index])
            data_index += 1

    # Calculate parity bits
    for bit_index in range(r):
        pos = 1 << bit_index
        parity = 0
        for k in range(1, n + 1):
            if k & pos and code[k - 1] == '1':
                parity ^= 1
        code[pos - 1] = str(parity)

    return ''.join(code)


def hamming_decodificar(codeword):
    """
    Args:
        codeword (str): bits recibidos (con posible error).
    Returns:
        tuple(str, bool, int): (mensaje_sin_paridad, hubo_error, posicion_error).
        posicion_error = 0 si no hubo error; el mensaje ya viene corregido.
    """
    n = len(codeword)

    # determine number of parity bits r (powers of two <= n)
    r = 0
    while (1 << r) <= n:
        r += 1

    # compute syndrome
    syndrome = 0
    for bit_index in range(r):
        pos = 1 << bit_index
        parity = 0
        for k in range(1, n + 1):
            if k & pos and codeword[k - 1] == '1':
                parity ^= 1
        if parity:
            syndrome += pos

    hubo_error = syndrome != 0
    posicion_error = syndrome if hubo_error else 0

    corrected = list(codeword)
    if hubo_error and 1 <= syndrome <= n:
        corrected[syndrome - 1] = '1' if corrected[syndrome - 1] == '0' else '0'

    # extract message bits (positions that are not powers of two)
    mensaje = []
    for k in range(1, n + 1):
        if (k & (k - 1)) != 0:
            mensaje.append(corrected[k - 1])

    return (''.join(mensaje), hubo_error, posicion_error)
