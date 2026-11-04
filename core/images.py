import base64
import binascii
import re

_DATA_URL_PATTERN = re.compile(r"^data:image/[a-zA-Z0-9.+-]+;base64,", re.IGNORECASE)
_WHITESPACE_PATTERN = re.compile(r"\s+")


class InvalidBase64ImageError(ValueError):
    """La imagen no contiene un valor base64 válido."""


class InvalidImageFormatError(ValueError):
    """La imagen no está en el formato esperado (WebP)."""


_WEBP_RIFF_OFFSET = 0
_WEBP_FORMAT_OFFSET = 8
_WEBP_MIN_BYTES = 12
_RIFF_MAGIC = b"RIFF"
_WEBP_MAGIC = b"WEBP"


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


def validate_webp_image(image_bytes: bytes) -> bytes:
    """Valida por magic bytes que los bytes correspondan a una imagen WebP.

    WebP es un contenedor RIFF: los primeros 4 bytes son "RIFF" y los bytes
    8..11 son "WEBP". Cualquier otro formato (PNG, JPEG, GIF, etc.) se rechaza.
    """
    if not isinstance(image_bytes, (bytes, bytearray)):
        raise InvalidImageFormatError("La imagen debe ser una cadena de bytes")

    if len(image_bytes) < _WEBP_MIN_BYTES:
        raise InvalidImageFormatError("La imagen está incompleta y no es un archivo WebP válido")

    if bytes(image_bytes[_WEBP_RIFF_OFFSET:_WEBP_RIFF_OFFSET + 4]) != _RIFF_MAGIC:
        raise InvalidImageFormatError("La imagen debe estar en formato WebP")

    if bytes(image_bytes[_WEBP_FORMAT_OFFSET:_WEBP_FORMAT_OFFSET + 4]) != _WEBP_MAGIC:
        raise InvalidImageFormatError("La imagen debe estar en formato WebP")

    return bytes(image_bytes)


def decode_and_validate_webp(value: str) -> bytes:
    """Decodifica base64 y valida que el resultado sea una imagen WebP."""
    return validate_webp_image(decode_base64_image(value))
