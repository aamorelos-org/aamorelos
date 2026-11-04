from database.database import Base
from sqlalchemy import Column, ForeignKey, VARCHAR


class Municipality(Base):
    __tablename__ = "municipios"
    id = Column(VARCHAR(10), primary_key=True)
    estado_id = Column(VARCHAR(10), ForeignKey("estados.id"), nullable=False)
    nombre = Column(VARCHAR(100), nullable=False)
