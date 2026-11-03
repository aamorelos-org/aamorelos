from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.images import decode_base64_image, InvalidBase64ImageError


class ReflexionResponseSchema(BaseModel):
    id: int
    slug: str
    title: str
    subtitle: str
    image: str
    alt: str
    url: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class ReflexionListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    data: list[ReflexionResponseSchema]


class ReflexionCreateSchema(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255, strip_whitespace=True)
    subtitle: str = Field(..., min_length=1, max_length=255, strip_whitespace=True)
    image: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1, max_length=10000, strip_whitespace=True)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        slug = value.strip()
        lowered = slug.lower()

        if not slug:
            raise ValueError("El slug no puede estar vacío")

        if "." in slug:
            raise ValueError('El slug no puede contener "."')

        if ".web" in lowered or "webp" in lowered:
            raise ValueError('El slug no puede contener ".web" ni "webp"')

        if any(char not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for char in lowered):
            raise ValueError("El slug solo puede contener minúsculas, números, guiones y guiones bajos")

        if slug != lowered:
            raise ValueError("El slug debe estar en minúsculas")

        return slug

    @field_validator("image")
    @classmethod
    def validate_image(cls, value: str) -> str:
        try:
            decode_base64_image(value)
        except InvalidBase64ImageError as exc:
            raise ValueError(str(exc)) from exc
        return value.strip()


class ReflexionCreateResponseSchema(BaseModel):
    ok: bool
    mensaje: str
    data: ReflexionResponseSchema
