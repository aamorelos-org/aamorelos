from database.database import Base
from sqlalchemy import CheckConstraint, Column, Integer, Text, VARCHAR


class Reflexion(Base):
    __tablename__ = "reflexiones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    slogan = Column(VARCHAR(100), unique=True, nullable=False)
    titulo = Column(VARCHAR(255), nullable=False)
    subtitulo = Column(VARCHAR(255), nullable=False)
    imagen = Column(Text, nullable=False)
    alt = Column(VARCHAR(255), nullable=False)
    url = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=False)
    es_activo = Column(VARCHAR(1), nullable=False, server_default="S")
    username = Column(VARCHAR(100), nullable=False, server_default="SYSTEM")

    __table_args__ = (
        CheckConstraint("es_activo IN ('S', 'N')", name="reflexiones_es_activo_sn_check"),
    )
