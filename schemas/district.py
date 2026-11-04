from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DistrictResponseSchema(BaseModel):
    id: str
    area_id: Optional[str] = None
    municipio_id: Optional[str] = None
    nombre: str
    distrito_numero: Optional[int] = None
    fecha_creacion: Optional[date] = None
    direccion: Optional[str] = None
    vecinos: Optional[str] = None
    codigo_postal: Optional[str] = None
    referencia: Optional[str] = None
    telefono: Optional[str] = None
    servicio_horas: Optional[str] = None
    es_activo: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DistrictByStateResponseSchema(DistrictResponseSchema):
    municipio: Optional[str] = None
    area: Optional[str] = None

    @classmethod
    def from_model(cls, d) -> "DistrictByStateResponseSchema":
        base_data = DistrictResponseSchema.model_validate(d).model_dump()
        base_data.update({
            "municipio": getattr(getattr(d, "municipio", None), "nombre", None),
            "area": getattr(getattr(d, "area", None), "nombre", None),
        })
        return cls.model_validate(base_data)


class DistrictListResponseSchema(BaseModel):
    ok: bool
    area_id: str
    total_registros: int
    data: list[DistrictResponseSchema]


class DistrictByStateListResponseSchema(DistrictListResponseSchema):
    estado_id: str
    area_id: Optional[str] = None
    data: list[DistrictByStateResponseSchema]


# Backward compatibility
DistrictSchema = DistrictResponseSchema
