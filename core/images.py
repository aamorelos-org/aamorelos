import base64
import binascii
import re

_DATA_URL_PATTERN = re.compile(r"^data:image/[a-zA-Z0-9.+-]+;base64,", re.IGNORECASE)
_WHITESPACE_PATTERN = re.compile(r"\s+")


class InvalidBase64ImageError(ValueError):
    """La imagen no contiene un valor base64 válido."""


def decode_base64_image(value: str) -> bytes:
    if not isinstance(value, str):
        raise InvalidBase64ImageError("La imagen debe enviarse como texto base64")

    candidate = value.strip()
    if not candidate:
        raise InvalidBase64ImageError("La imagen no puede estar vacía")

    if _DATA_URL_PATTERN.match(candidate):
        candidate = candidate.split(",", 1)[1]
    elif candidate.startswith("data:"):
        raise InvalidBase64ImageError("El data URL debe ser de tipo image/* y codificarse en base64")

    candidate = _WHITESPACE_PATTERN.sub("", candidate)

    try:
        image_bytes = base64.b64decode(candidate, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise InvalidBase64ImageError("La imagen no contiene un base64 válido") from exc

    if not image_bytes:
        raise InvalidBase64ImageError("La imagen no contiene datos")

    return image_bytes
