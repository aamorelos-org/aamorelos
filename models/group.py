from database.database import Base
from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, Text, VARCHAR
from sqlalchemy.orm import relationship


class Group(Base):
    __tablename__ = "grupos"
    id = Column(VARCHAR(50), primary_key=True)
    distrito_id = Column(VARCHAR(50), ForeignKey("distritos.id"), nullable=False)
    municipio_id = Column(VARCHAR(10), ForeignKey("municipios.id"), nullable=False)
    tipo_id = Column(Integer, ForeignKey("grupos_tipos.id"))
    lengua_id = Column(Integer, ForeignKey("lenguas.id"))
    genero_id = Column(Integer, ForeignKey("grupos_generos.id"))

    nombre = Column(Text, nullable=False)
    fecha_creacion = Column(Date)
    direccion = Column(Text)
    vecinos = Column(VARCHAR(100))
    codigo_postal = Column(VARCHAR(10))
    referencias = Column(Text)
    localidad = Column(VARCHAR(100))
    cpr = Column(VARCHAR(50))
    horario_lunes = Column(Text)
    horario_martes = Column(Text)
    horario_miercoles = Column("horario_miércoles", Text)
    horario_jueves = Column(Text)
    horario_viernes = Column(Text)
    horario_sabado = Column(Text)
    horario_domingo = Column(Text)
    horario_observacion = Column(Text)
    lenguaje_detalle = Column(Text)
    permite_fumar = Column(Integer)
    es_activo = Column(Integer)
    latitud = Column("latitude", Numeric(10, 8))
    longitud = Column("longitude", Numeric(11, 8))
    fumar_texto = Column("fumar_texto", VARCHAR(50))

    distrito = relationship("District")
    municipio = relationship("Municipality")
    grupo_tipo = relationship("GroupType")
    lengua = relationship("Language")
    genero = relationship("GroupGender")
