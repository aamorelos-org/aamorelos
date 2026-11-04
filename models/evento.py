from database.database import Base
from sqlalchemy import CheckConstraint, Column, Integer, Text, VARCHAR
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(VARCHAR(50), nullable=False)
    slogan = Column(VARCHAR(100), unique=True, nullable=False)
    url = Column(Text)
    titulo = Column(VARCHAR(255), nullable=False)
    subtitulo = Column(VARCHAR(255))
    imagen = Column(Text, nullable=False)
    alt = Column(VARCHAR(255))
    pie = Column(VARCHAR(255))
    frases = Column(JSONB)
    es_activo = Column(VARCHAR(1), nullable=False, server_default="S")
    username = Column(VARCHAR(100), nullable=False, server_default="SYSTEM")

    aniversario = relationship("Aniversario", back_populates="evento", uselist=False)

    __table_args__ = (
        CheckConstraint("es_activo IN ('S', 'N')", name="eventos_es_activo_sn_check"),
    )
