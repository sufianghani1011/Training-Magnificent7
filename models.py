from sqlalchemy import Column, Integer, String, Float
from database import Base

class Books(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    published_year = Column(Integer, nullable=False)
    genre = Column(String, nullable=True, default="General")
    price = Column(Float, nullable=True, default=0.0)
