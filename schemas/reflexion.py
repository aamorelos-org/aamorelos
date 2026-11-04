from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.images import (
    InvalidBase64ImageError,
    InvalidImageFormatError,
    decode_and_validate_webp,
)
from core.slugs import validate_slogan


class ReflexionListItemSchema(BaseModel):
    id: int
    slogan: str
    titulo: str
    subtitulo: str
    imagen: str
    alt: str
    url: str

    model_config = ConfigDict(from_attributes=True)


class ReflexionResponseSchema(BaseModel):
    id: int
    slogan: str
    titulo: str
    subtitulo: str
    imagen: str
    alt: str
    url: str
    descripcion: str

    model_config = ConfigDict(from_attributes=True)


class ReflexionListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    data: list[ReflexionListItemSchema]


class ReflexionDetailResponseSchema(BaseModel):
    ok: bool
    data: ReflexionResponseSchema


class ReflexionCreateSchema(BaseModel):
    slogan: str = Field(..., min_length=1, max_length=100)
    titulo: str = Field(..., min_length=1, max_length=255, strip_whitespace=True)
    subtitulo: str = Field(..., min_length=1, max_length=255, strip_whitespace=True)
    imagen: str = Field(..., min_length=1)
    descripcion: str = Field(..., min_length=1, max_length=10000, strip_whitespace=True)

    @field_validator("slogan")
    @classmethod
    def validate_slogan(cls, value: str) -> str:
        return validate_slogan(value)

    @field_validator("imagen")
    @classmethod
    def validate_imagen(cls, value: str) -> str:
        try:
            decode_and_validate_webp(value)
        except (InvalidBase64ImageError, InvalidImageFormatError) as exc:
            raise ValueError(str(exc)) from exc
        return value.strip()


class ReflexionCreateResponseSchema(BaseModel):
    ok: bool
    mensaje: str
    data: ReflexionResponseSchema
