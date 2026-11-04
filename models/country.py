from database.database import Base
from sqlalchemy import Column, VARCHAR


class Country(Base):
    __tablename__ = "paises"
    id = Column(VARCHAR(10), primary_key=True)
    nombre = Column(VARCHAR(100), unique=True, nullable=False)
    codigo = Column(VARCHAR(3), unique=True)
