from database.database import Base
from sqlalchemy import Column, ForeignKey, Integer, Text, VARCHAR
from sqlalchemy.dialects.postgresql import BIT
from sqlalchemy.orm import relationship


class Aniversario(Base):
    __tablename__ = "aniversarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    evento_id = Column(Integer, ForeignKey("eventos.id", ondelete="CASCADE"), nullable=False, unique=True)
    epigrafe = Column(Text, nullable=False)
    kicker = Column(VARCHAR(100), nullable=False)
    frase_reflexion = Column(Text, nullable=False)
    sede = Column(VARCHAR(100), nullable=False)
    dias_unidad = Column(VARCHAR(100), nullable=False)
    junta_publica = Column(VARCHAR(100), nullable=False)
    contacto_nombre = Column(VARCHAR(100), nullable=False)
    contacto_telefono = Column(VARCHAR(100), nullable=False)

    evento = relationship("Evento", back_populates="aniversario")
    dias = relationship("AniversarioDia", back_populates="aniversario", cascade="all, delete-orphan", order_by="AniversarioDia.id")


class AniversarioDia(Base):
    __tablename__ = "aniversarios_dias"
    id = Column(Integer, primary_key=True, autoincrement=True)
    aniversario_id = Column(Integer, ForeignKey("aniversarios.id", ondelete="CASCADE"), nullable=False)
    dia = Column(VARCHAR(100), nullable=False)
    tema = Column(VARCHAR(100), nullable=False)
    fecha = Column(VARCHAR(100), nullable=False)
    grupos = Column(VARCHAR(255), nullable=False)
    numero = Column(VARCHAR(2), nullable=False)
    es_junta_publica = Column(BIT(1), nullable=False)

    aniversario = relationship("Aniversario", back_populates="dias")
