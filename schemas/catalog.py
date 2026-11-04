from typing import Optional
from datetime import date

from pydantic import BaseModel, ConfigDict


class CatalogSchema(BaseModel):
    id: int | str
    nombre: str

    model_config = ConfigDict(from_attributes=True)


class CatalogListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    data: list[CatalogSchema]


class CountrySchema(BaseModel):
    id: str
    nombre: str
    codigo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CountryListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    data: list[CountrySchema]


class RegionSchema(BaseModel):
    id: str
    nombre: str

    model_config = ConfigDict(from_attributes=True)


class RegionListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    data: list[RegionSchema]


class StateSchema(BaseModel):
    id: str
    nombre: str
    pais_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StateListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    pais_id: Optional[str] = None
    data: list[StateSchema]


class AreaSchema(BaseModel):
    id: str
    region_id: Optional[str] = None
    municipio_id: Optional[str] = None
    nombre: str
    fecha_creacion: Optional[date] = None
    direccion: Optional[str] = None
    vecinos: Optional[str] = None
    codigo_postal: Optional[str] = None
    referencias: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    servicio_horas: Optional[str] = None
    es_activo: Optional[int] = None
    sitio_web: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AreaListResponseSchema(BaseModel):
    ok: bool
    region_id: Optional[str] = None
    estado_id: Optional[str] = None
    total_registros: int
    data: list[AreaSchema]


class GroupGenderSchema(CatalogSchema):
    pass


class GroupTypeSchema(CatalogSchema):
    pass


class LanguageSchema(CatalogSchema):
    pass
