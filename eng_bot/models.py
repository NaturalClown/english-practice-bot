from datetime import datetime

from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass 

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(BigInteger ,primary_key=True)
    level: Mapped[str | None] = mapped_column(String(3), nullable=True)
    
    skills: Mapped[list['Skill']] = relationship(back_populates='user')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_activity: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    


class Skill(Base):
    __tablename__ = 'skills'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='skills')
    
    get_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
