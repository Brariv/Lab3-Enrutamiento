def codificar_mensaje(texto):
    """
    Codifica cada carácter de texto a su ASCII binario de 8 bits.

    Args:
        texto (str): mensaje en texto plano.
    Returns:
        str: string de bits, ej. "A" -> "01000001"
    """
    return "".join(format(ord(c), "08b") for c in texto)


def decodificar_mensaje(binario, hay_error):
    """
    Decodifica un string de bits (múltiplos de 8) a texto.

    Args:
        binario (str): bits del mensaje, sin bits de redundancia.
        hay_error (bool): si True, no se pudo garantizar integridad.
    Returns:
        str | None: texto decodificado, o None si hay_error es True
                     (capas/aplicacion.py debe mostrar el error en ese caso).
    """
    if hay_error:
        return None
    caracteres = [binario[i:i + 8] for i in range(0, len(binario), 8)]
    return "".join(chr(int(b, 2)) for b in caracteres)
