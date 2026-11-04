from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GroupResponseSchema(BaseModel):
    id: str
    distrito_id: str
    municipio_id: str
    tipo_id: Optional[int] = None
    lengua_id: Optional[int] = None
    genero_id: Optional[int] = None
    nombre: str
    fecha_creacion: Optional[date] = None
    direccion: Optional[str] = None
    vecinos: Optional[str] = None
    codigo_postal: Optional[str] = None
    referencias: Optional[str] = None
    localidad: Optional[str] = None
    cpr: Optional[str] = None

    horario_lunes: Optional[str] = None
    horario_martes: Optional[str] = None
    horario_miercoles: Optional[str] = None
    horario_jueves: Optional[str] = None
    horario_viernes: Optional[str] = None
    horario_sabado: Optional[str] = None
    horario_domingo: Optional[str] = None
    horario_observacion: Optional[str] = None

    lenguaje_detalle: Optional[str] = None
    permite_fumar: Optional[int] = None
    es_activo: Optional[int] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    fumar_texto: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GroupEnrichedResponseSchema(GroupResponseSchema):
    municipio: Optional[str] = None
    tipo: Optional[str] = None
    genero: Optional[str] = None
    lengua: Optional[str] = None

    @classmethod
    def from_model(cls, g) -> "GroupEnrichedResponseSchema":
        base_data = GroupResponseSchema.model_validate(g).model_dump()
        base_data.update({
            "municipio": getattr(getattr(g, "municipio", None), "nombre", None),
            "tipo": getattr(getattr(g, "grupo_tipo", None), "nombre", None),
            "genero": getattr(getattr(g, "genero", None), "nombre", None),
            "lengua": getattr(getattr(g, "lengua", None), "nombre", None),
        })
        return cls.model_validate(base_data)


# Backward compatibility aliases
GroupByDistrictResponseSchema = GroupEnrichedResponseSchema
GroupByStateResponseSchema = GroupEnrichedResponseSchema


class GroupListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    skip: int
    limit: int
    data: list[GroupEnrichedResponseSchema]


class GroupByDistrictListResponseSchema(BaseModel):
    ok: bool
    distrito_id: str
    total_registros: int
    data: list[GroupEnrichedResponseSchema]


class GroupByStateListResponseSchema(BaseModel):
    ok: bool
    estado_id: str
    distrito_id: Optional[str] = None
    total_registros: int
    data: list[GroupEnrichedResponseSchema]
