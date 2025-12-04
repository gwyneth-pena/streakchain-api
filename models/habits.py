

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from db import Base


class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = (
        CheckConstraint('frequency >= 0 AND frequency <= 31', name='check_frequency'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    frequency = Column(Integer, nullable=False, default=0)
    color = Column(String(40), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship('User', back_populates='habits')
    logs = relationship('HabitLog', back_populates='habit', cascade='all, delete-orphan')