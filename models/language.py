from database.database import Base
from sqlalchemy import Column, Integer, VARCHAR


class Language(Base):
    __tablename__ = "lenguas"
    id = Column(Integer, primary_key=True)
    nombre = Column(VARCHAR(100), unique=True, nullable=False)
