from database.database import Base
from sqlalchemy import Column, Date, ForeignKey, Integer, Text, VARCHAR


class Area(Base):
    __tablename__ = "areas"
    id = Column(VARCHAR(10), primary_key=True)
    region_id = Column(VARCHAR(10), ForeignKey("regiones.id"))
    municipio_id = Column(VARCHAR(10), ForeignKey("municipios.id"), nullable=False)
    nombre = Column(Text, nullable=False)
    fecha_creacion = Column(Date)
    direccion = Column(Text)
    vecinos = Column(VARCHAR(100))
    codigo_postal = Column(VARCHAR(10))
    referencias = Column(Text)
    telefono = Column(VARCHAR(50))
    correo = Column(VARCHAR(100))
    servicio_horas = Column(Text)
    es_activo = Column(Integer)
    sitio_web = Column(Text)
