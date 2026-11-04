from database.database import Base
from sqlalchemy import Column, Integer, VARCHAR


class GroupGender(Base):
    __tablename__ = "grupos_generos"
    id = Column(Integer, primary_key=True)
    nombre = Column(VARCHAR(100), unique=True, nullable=False)
