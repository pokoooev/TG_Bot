from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    thread_id = Column(String(255), nullable=True)

    # Связи
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id})>"


class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
    
    # Индексы для быстрого поиска
    __table_args__ = (
        Index('idx_conversations_user_id', 'user_id'),
        Index('idx_conversations_created_at', 'created_at'),
    )
    
    # Связи
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"


class Cache(Base):
    __tablename__ = 'cache'
    
    question_hash = Column(String(64), primary_key=True)  
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    hits = Column(Integer, default=1)  
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cache_hits', 'hits'),
    )
    
    def __repr__(self):
        return f"<Cache(question_hash={self.question_hash}, hits={self.hits})>"