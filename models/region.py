from database.database import Base
from sqlalchemy import Column, VARCHAR


class Region(Base):
    __tablename__ = "regiones"
    id = Column(VARCHAR(10), primary_key=True)
    nombre = Column(VARCHAR(100), nullable=False)
