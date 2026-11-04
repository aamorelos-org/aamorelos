from database.database import Base
from sqlalchemy import Column, ForeignKey, VARCHAR


class State(Base):
    __tablename__ = "estados"
    id = Column(VARCHAR(10), primary_key=True)
    pais_id = Column("estado_id", VARCHAR(10), ForeignKey("paises.id"), nullable=False)
    nombre = Column(VARCHAR(100), nullable=False)
