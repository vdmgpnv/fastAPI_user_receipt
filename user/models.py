from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime



class User(Base):
    """Таблица пользователей"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    creation_date = Column(DateTime, default=datetime.now())
    update_date = Column(DateTime, nullable=True, default=datetime.now())
    receipts = relationship("Receipt", back_populates='user', passive_deletes=True)
    likes = relationship('Likes', back_populates='user', passive_deletes=True)
    favourites = relationship('Favourites', back_populates='user', passive_deletes=True)
    