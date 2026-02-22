import asyncio
import os
from yandex_ai_studio_sdk import AIStudio
from dotenv import load_dotenv

from yandex_gpt.create_assistant import update_assistant

load_dotenv()

FOLDER_ID = os.getenv("FOLDER_ID")
API_KEY = os.getenv("API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
INDEX_ID = os.getenv("INDEX_ID")

sdk = AIStudio(folder_id=FOLDER_ID, auth=API_KEY)
detailed_instruction = """Ты — эксперт по API Битрикс24. Твоя задача — помогать разработчикам с полными и точными ответами.
Отвечай на вопрос подробно, задавай уточняющие вопросы и сохраняй контекст беседы, запоминая о какой сущности речь"""
update_assistant(ASSISTANT_ID, instruction=detailed_instruction)

def create_thread():
    """Создает новый тред"""
    return sdk.threads.create(ttl_days=1, expiration_policy="static")

class YandexAssistantClient:
    def __init__(self):
        if not ASSISTANT_ID:
            raise ValueError("ASSISTANT_ID не указан в .env файле")
        
    
        self.assistant = sdk.assistants.get(ASSISTANT_ID)
        

        if INDEX_ID:
            search_tool = sdk.tools.search_index(INDEX_ID)
            self.assistant = self.assistant.update(tools=[search_tool])
        
    
    
    def ask(self, question: str, thread_id: str = None) -> tuple:
        """Задать вопрос ассистенту"""
        print(f"Вопрос: {question}")
        print(f"Thread ID: {thread_id}")
        try:
    
            
            if thread_id:
                thread = sdk.threads.get(thread_id)
                print(f"Тред НАЙДЕН: {thread.id}")
            else:
                print(f"THREAD_ID нет, создаю новый")
                thread = sdk.threads.create(ttl_days=1, expiration_policy="static")
            
            thread.write(question)

            run = self.assistant.run(thread)
            
            result = run.wait()
            
            messages = result.text

            print(f"ОТВЕТ: {result.text[:100]}...")
            print(f"НОВЫЙ THREAD_ID: {thread.id}")

            return messages, thread.id
            
            
    
            
        except Exception as e:
            print(f"Ошибка: {e}")
            return f"Произошла ошибка: {e}",  thread_id if thread_id else None
    
    async def ask_async(self, question: str, thread_id: str = None) -> tuple:
        """Асинхронная обертка для бота"""
        try:
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
            None, 
            lambda: self.ask(question, thread_id)  
        )
            return result
        except Exception as e:
            print(f"Асинхронная ошибка: {e}")
            return f"Произошла ошибка: {e}"