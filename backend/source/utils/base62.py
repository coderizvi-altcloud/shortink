"""Base62 helpers for short code generation."""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)


def encode_base62(value: int) -> str:
    if value < 0:
        raise ValueError("Base62 encoding requires a non-negative integer")
    if value == 0:
        return ALPHABET[0]

    encoded = []
    while value > 0:
        value, remainder = divmod(value, BASE)
        encoded.append(ALPHABET[remainder])
    return "".join(reversed(encoded))
