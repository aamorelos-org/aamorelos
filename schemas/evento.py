from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.images import (
    InvalidBase64ImageError,
    InvalidImageFormatError,
    decode_and_validate_webp,
)
from core.slugs import validate_slogan


class EventoListItemSchema(BaseModel):
    id: int
    tipo: str
    slogan: str
    url: Optional[str] = None
    titulo: str
    subtitulo: Optional[str] = None
    imagen: str
    alt: Optional[str] = None
    pie: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EventoResponseSchema(EventoListItemSchema):
    frases: Optional[Any] = None


class AniversarioDiaSchema(BaseModel):
    dia: str
    tema: str
    fecha: str
    grupos: str
    numero: str
    es_junta_publica: bool

    model_config = ConfigDict(from_attributes=True)


class AniversarioSchema(BaseModel):
    epigrafe: str
    kicker: str
    frase_reflexion: str
    sede: str
    dias_unidad: str
    junta_publica: str
    contacto_nombre: str
    contacto_telefono: str
    dias: list[AniversarioDiaSchema] = []

    model_config = ConfigDict(from_attributes=True)


class EventoDetailDataSchema(EventoResponseSchema):
    aniversario: Optional[AniversarioSchema] = None


class EventoListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    skip: int
    limit: int
    data: list[EventoListItemSchema]


class EventoDetailResponseSchema(BaseModel):
    ok: bool
    data: EventoDetailDataSchema


class EventoDiaCreateSchema(BaseModel):
    dia: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    tema: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    fecha: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    grupos: str = Field(..., min_length=1, max_length=255, strip_whitespace=True)
    numero: str = Field(..., min_length=1, max_length=2, strip_whitespace=True)
    es_junta_publica: bool = False


class EventoCreateBaseSchema(BaseModel):
    slogan: str = Field(..., min_length=1, max_length=100)
    titulo: str = Field(..., min_length=1, max_length=255, strip_whitespace=True)
    subtitulo: Optional[str] = Field(None, max_length=255, strip_whitespace=True)
    imagen: str = Field(..., min_length=1)
    pie: Optional[str] = Field(None, max_length=255, strip_whitespace=True)

    @field_validator("slogan")
    @classmethod
    def _check_slogan(cls, value: str) -> str:
        return validate_slogan(value)

    @field_validator("imagen")
    @classmethod
    def _check_imagen(cls, value: str) -> str:
        try:
            decode_and_validate_webp(value)
        except (InvalidBase64ImageError, InvalidImageFormatError) as exc:
            raise ValueError(str(exc)) from exc
        return value.strip()


class InformativoCreateSchema(EventoCreateBaseSchema):
    tipo: Literal["informativo"]
    parrafo1: str = Field("", max_length=10000, strip_whitespace=True)
    parrafo2: str = Field("", max_length=10000, strip_whitespace=True)


class AniversarioCreateSchema(EventoCreateBaseSchema):
    tipo: Literal["aniversario"]
    epigrafe: str = Field(..., min_length=1, strip_whitespace=True)
    kicker: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    frase_reflexion: str = Field(..., min_length=1, strip_whitespace=True)
    sede: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    dias_unidad: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    junta_publica: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    contacto_nombre: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    contacto_telefono: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    dias: List[EventoDiaCreateSchema] = Field(default_factory=list)


EventoCreateSchema = Annotated[
    Union[InformativoCreateSchema, AniversarioCreateSchema],
    Field(discriminator="tipo"),
]


class EventoCreateResponseSchema(BaseModel):
    ok: bool
    mensaje: str
    data: EventoDetailDataSchema


class AdminEventoListItemSchema(BaseModel):
    id: int
    tipo: str
    slogan: str
    url: Optional[str] = None
    titulo: str
    subtitulo: Optional[str] = None
    imagen: str
    alt: Optional[str] = None
    pie: Optional[str] = None
    es_activo: str

    model_config = ConfigDict(from_attributes=True)


class AdminEventoResponseSchema(AdminEventoListItemSchema):
    frases: Optional[Any] = None


class AdminEventoDetailDataSchema(AdminEventoResponseSchema):
    aniversario: Optional[AniversarioSchema] = None


class AdminEventoListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    skip: int
    limit: int
    data: list[AdminEventoListItemSchema]


class AdminEventoDetailResponseSchema(BaseModel):
    ok: bool
    data: AdminEventoDetailDataSchema


class AdminEventoCreateResponseSchema(BaseModel):
    ok: bool
    mensaje: str
    data: AdminEventoDetailDataSchema


class EventoEstadoUpdateSchema(BaseModel):
    es_activo: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("es_activo")
    @classmethod
    def validate_es_activo(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if cleaned not in {"S", "N"}:
            raise ValueError("es_activo debe ser 'S' o 'N'")
        return cleaned


class AdminEventoStatusResponseSchema(BaseModel):
    ok: bool
    mensaje: str
    data: AdminEventoDetailDataSchema
