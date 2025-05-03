from sqlalchemy import Column, Integer, String
from app.shared.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String(50))
    first_name = Column(String(100))
    last_name = Column(String(100))