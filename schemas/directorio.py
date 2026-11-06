from typing import Optional

from pydantic import BaseModel, ConfigDict


class DirectorioListItemSchema(BaseModel):
    id: int
    pagina: int
    imagen: str
    anio: Optional[str] = None
    mes: str

    model_config = ConfigDict(from_attributes=True)


class DirectorioListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    data: list[DirectorioListItemSchema]
