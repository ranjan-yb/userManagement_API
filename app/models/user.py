from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)   # no unique=True, no index=True if you don’t need it
    email = Column(String, unique=True, index=True)
    password = Column(String(100))  # Store hashed password, adjust length as needed