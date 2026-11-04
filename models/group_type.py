from database.database import Base
from sqlalchemy import Column, Integer, VARCHAR


class GroupType(Base):
    __tablename__ = "grupos_tipos"
    id = Column(Integer, primary_key=True)
    nombre = Column(VARCHAR(100), unique=True, nullable=False)
