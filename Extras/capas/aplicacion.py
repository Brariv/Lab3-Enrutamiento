def solicitar_mensaje(mensaje):
    """
    Solicita un mensaje al usuario y lo devuelve.

    Args:
        mensaje (str): El mensaje que se mostrará al usuario.

    Returns:
        str: El mensaje ingresado por el usuario.
    """
    return input(mensaje)


def solicitar_algoritmo():
    """
    Pide al usuario el algoritmo de integridad a usar.

    Returns:
        str: "hamming" | "fletcher" | "crc32"
    """
    return input("Algoritmo de integridad (hamming/fletcher/crc32): ").strip().lower()


def mostrar_mensaje(mensaje, error=False):
    """
    Muestra un mensaje al usuario. Si error es True, se indica que no fue
    posible corregir/verificar el mensaje.

    Args:
        mensaje (str): El mensaje que se mostrará al usuario.
        error (bool): Si True, se imprime como error en lugar del mensaje.
    """
    if error:
        print(">> ERROR: mensaje recibido con errores no corregibles")
    else:
        print(mensaje)
