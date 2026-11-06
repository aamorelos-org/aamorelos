from database.database import Base
from sqlalchemy import TIMESTAMP, Column, Integer, VARCHAR
from sqlalchemy.sql import func


class Directorio(Base):
    __tablename__ = "directorio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pagina = Column(Integer, nullable=False)
    imagen = Column(VARCHAR(255), nullable=False)
    anio = Column(VARCHAR(4), nullable=False, server_default="2026")
    mes = Column(VARCHAR(20), nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
