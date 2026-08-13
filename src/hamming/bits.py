"""Conversion entre texto (UTF-8) y cadenas de bits ('0'/'1')."""


def text_to_bits(text: str) -> str:
    return "".join(f"{byte:08b}" for byte in text.encode("utf-8"))


def bits_to_text(bits: str) -> str:
    if len(bits) % 8 != 0:
        raise ValueError("la cantidad de bits debe ser multiplo de 8 para reconstruir texto")
    byte_chunks = [bits[i:i + 8] for i in range(0, len(bits), 8)]
    byte_values = bytes(int(chunk, 2) for chunk in byte_chunks)
    return byte_values.decode("utf-8")
