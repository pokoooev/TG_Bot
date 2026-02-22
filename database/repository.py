from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import hashlib
from typing import Optional, List
from .models import User, Conversation, Cache

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_or_create(self, telegram_id: int, user_data: dict) -> User:
        """Получить пользователя или создать нового"""
        # Ищем существующего
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            return user
        
        # Создаем нового
        user = User(
            telegram_id=telegram_id,
            username=user_data.get('username'),
            first_name=user_data.get('first_name')
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID в БД"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_users(self, limit: int = 100) -> List[User]:
        """Получить всех пользователей"""
        result = await self.session.execute(
            select(User).limit(limit)
        )
        return result.scalars().all()


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add(self, user_id: int, question: str, answer: str) -> Conversation:
        """Добавить новый диалог"""
        conversation = Conversation(
            user_id=user_id,
            question=question,
            answer=answer,
            created_at=datetime.utcnow()
        )
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation
    
    async def get_user_history(self, user_id: int, limit: int = 10) -> List[Conversation]:
        """Получить историю диалогов пользователя"""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_id(self, conv_id: int) -> Optional[Conversation]:
        """Получить диалог по ID"""
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conv_id)
        )
        return result.scalar_one_or_none()
    
    async def get_recent_all(self, limit: int = 50) -> List[Conversation]:
        """Получить последние диалоги всех пользователей"""
        result = await self.session.execute(
            select(Conversation)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


class CacheRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, question: str) -> Optional[str]:
        """Получить ответ из кэша"""
        question_hash = hashlib.md5(question.encode()).hexdigest()
        
        result = await self.session.execute(
            select(Cache).where(Cache.question_hash == question_hash)
        )
        cache = result.scalar_one_or_none()
        
        if cache:
            cache.hits += 1
            await self.session.commit()
            return cache.answer
        
        return None
    
    async def set(self, question: str, answer: str) -> Cache:
        """Сохранить ответ в кэш"""
        
        question_hash = hashlib.md5(question.encode()).hexdigest()
        
        
        result = await self.session.execute(
            select(Cache).where(Cache.question_hash == question_hash)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            
            existing.answer = answer
            existing.hits += 1
            existing.created_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        else:
    
            cache = Cache(
                question_hash=question_hash,
                question=question,
                answer=answer,
                hits=1,
                created_at=datetime.utcnow()
            )
            self.session.add(cache)
            await self.session.commit()
            await self.session.refresh(cache)
            return cache
    
    async def get_popular(self, limit: int = 10) -> List[Cache]:
        """Получить популярные вопросы (по количеству использований)"""
        result = await self.session.execute(
            select(Cache)
            .order_by(Cache.hits.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_by_question(self, text: str, limit: int = 10) -> List[Cache]:
        """Поиск по тексту вопроса"""
        result = await self.session.execute(
            select(Cache)
            .where(Cache.question.ilike(f'%{text}%'))
            .order_by(Cache.hits.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def clear_old(self, days: int = 30) -> int:
        """Удалить старые записи из кэша """
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            delete(Cache).where(Cache.created_at < cutoff)
        )
        await self.session.commit()
        return result.rowcount