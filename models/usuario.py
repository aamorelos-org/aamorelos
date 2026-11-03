from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.sql import func

from database.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(150), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    actualizado_en = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class HistorialLogin(Base):
    __tablename__ = "historial_logins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha_login = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    exitoso = Column(Boolean, default=True)
