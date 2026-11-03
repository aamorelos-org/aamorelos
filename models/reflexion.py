from database.database import Base
from sqlalchemy import Column, Integer, Text, VARCHAR


class Reflexion(Base):
    __tablename__ = "reflexiones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(VARCHAR(100), unique=True, nullable=False)
    title = Column(VARCHAR(255), nullable=False)
    subtitle = Column(VARCHAR(255), nullable=False)
    image = Column(Text, nullable=False)
    alt = Column(VARCHAR(255), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
