from email.policy import default
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, null
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime


class Receipt(Base):
    """Таблица рецептов"""
    __tablename__ = 'receipts'
    id = Column(Integer, primary_key=True, index=True)
    creation_date = Column(DateTime, default=datetime.now())
    update_date = Column(DateTime, nullable=True, default=datetime.now())
    name = Column(String)
    description = Column(String)
    cookie_steps = Column(String)
    image = Column(String, default=None)
    dish_type = Column(Integer, ForeignKey('dishes.id'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('User', back_populates='receipts', cascade="all,delete")
    hashtags = Column(String)
    is_active = Column(Boolean, default=True)
    likes = relationship('Likes', back_populates='receipt', passive_deletes=True)
    favourites = relationship('Favourites', back_populates='receipt', passive_deletes=True)
    
class DishType(Base):
    """Таблица с типами блюд"""
    __tablename__ = 'dishes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Likes(Base):
    """Таблица для связи многие ко многим, для реализации лайков"""
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receipt_id = Column(
        Integer, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship('User', back_populates='likes')
    receipt = relationship('Receipt', back_populates='likes')
    
class Favourites(Base):
    """Таблица для связи многие ко многим, для реализации избранного"""
    __tablename__ = 'favourites'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receipt_id = Column(
        Integer, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship('User', back_populates='favourites')
    receipt = relationship('Receipt', back_populates='favourites')