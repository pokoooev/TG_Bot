import sys
import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import AsyncSessionLocal
from database.repository import UserRepository, ConversationRepository, CacheRepository
from yandex_client import YandexAssistantClient


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

yandex_client = YandexAssistantClient()

# Функция для получения репозиториев
async def get_repositories():
    session = AsyncSessionLocal()
    try:
        user_repo = UserRepository(session)
        conv_repo = ConversationRepository(session)
        cache_repo = CacheRepository(session)
        return session, user_repo, conv_repo, cache_repo
    except:
        await session.close()
        raise

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    session, user_repo, conv_repo, cache_repo = await get_repositories()
    try:
        db_user = await user_repo.get_or_create(
            telegram_id=user.id,
            user_data={
                'username': user.username,
                'first_name': user.first_name
            }
        )
        
        await update.message.reply_text(
            f"Привет, {user.first_name}!\n\n"
            "Я бот-помощник по API Битрикс24.\n"
            "Задавай мне любые вопросы по документации!"
        )
    finally:
        await session.close()

# Обработчик текстовых сообщений
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    user = update.effective_user
    
    
    await update.message.chat.send_action(action='typing')
    
    session, user_repo, conv_repo, cache_repo = await get_repositories()
    try:
        # Получаем пользователя из БД
        db_user = await user_repo.get_by_telegram_id(user.id)
        if not db_user:
            db_user = await user_repo.get_or_create(
                telegram_id=user.id,
                user_data={
                    'username': user.username,
                    'first_name': user.first_name
                }
            )
        
        
        cached_answer = await cache_repo.get(question)
        
        if cached_answer:
            answer = cached_answer
            source = "Ответ из кэша"
            # Для кэша не обновляем thread_id
            new_thread_id = db_user.thread_id if hasattr(db_user, 'thread_id') else None
        else:
            # Вызываем ассистента с thread_id из БД
            thread_id = getattr(db_user, 'thread_id', None)
            print(f"БЕРУ ИЗ БД thread_id: {thread_id}")
            
            
            result = await yandex_client.ask_async(question, thread_id=thread_id)
            
            
            if isinstance(result, tuple) and len(result) == 2:
                answer, new_thread_id = result
            else:
                
                answer = str(result)
                new_thread_id = thread_id
            
            source = "Ответ"
            
        
            if hasattr(db_user, 'thread_id') and db_user.thread_id != new_thread_id:
                db_user.thread_id = new_thread_id
                await session.commit()
            
            if answer and not answer.startswith("Произошла ошибка"):
                await cache_repo.set(question, answer)
        
        
        await conv_repo.add(
            user_id=db_user.id,
            question=question,
            answer=answer
        )
        
        # Отправляем ответ
        await update.message.reply_text(f"{source}\n\n{answer}")
        
    finally:
        await session.close()

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

def main():
    """Запуск бота"""
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
    application.add_error_handler(error_handler)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()