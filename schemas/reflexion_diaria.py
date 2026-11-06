from pydantic import BaseModel, ConfigDict


class ReflexionDiariaListItemSchema(BaseModel):
    id: int
    fecha: str
    titulo: str
    texto: str
    cita: str
    contenido: str

    model_config = ConfigDict(from_attributes=True)


class ReflexionDiariaListResponseSchema(BaseModel):
    ok: bool
    total_registros: int
    fecha: str
    data: list[ReflexionDiariaListItemSchema]
