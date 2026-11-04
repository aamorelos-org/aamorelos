from database.database import Base
from sqlalchemy import Column, Date, ForeignKey, Integer, Text, VARCHAR
from sqlalchemy.orm import relationship


class District(Base):
    __tablename__ = "distritos"
    id = Column(VARCHAR(50), primary_key=True)
    area_id = Column(VARCHAR(10), ForeignKey("areas.id"), nullable=False)
    municipio_id = Column(VARCHAR(10), ForeignKey("municipios.id"), nullable=False)
    nombre = Column(Text, nullable=False)
    distrito_numero = Column(Integer)
    fecha_creacion = Column(Date)
    direccion = Column(Text)
    vecinos = Column(VARCHAR(100))
    codigo_postal = Column(VARCHAR(10))
    referencia = Column(Text)
    telefono = Column(VARCHAR(50))
    servicio_horas = Column(Text)
    es_activo = Column(Integer)

    municipio = relationship("Municipality")
    area = relationship("Area")
