from database.database import Base
from sqlalchemy import TIMESTAMP, Column, Integer, Text, VARCHAR
from sqlalchemy.sql import func


class ReflexionDiaria(Base):
    __tablename__ = "reflexiones_diarias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(VARCHAR(5), nullable=False)
    titulo = Column(Text, nullable=False)
    texto = Column(Text, nullable=False)
    cita = Column(Text, nullable=False)
    contenido = Column(Text, nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
