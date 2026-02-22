## Структура проекта

```
BOT_TG/
├── .env                         # Переменные окружения
├── .gitignore                   # Игнорируемые файлы
├── README.md                    # Документация
├── requirements.txt              # Зависимости
├── schedule.py                    # Планировщик
├── yandex_client.py                # Клиент Yandex Assistant
│
├── alembic/                       # Миграции БД
│   └── versions/                   # Версии миграций
│
├── database/                       # Работа с БД
│   ├── __init__.py
│   ├── db.py                        # Подключение к БД
│   ├── models.py                     # Модели SQLAlchemy
│   └── repository.py                  # Репозитории (CRUD)
│
├── knowledge_base/                    # Документация
│
├── logs/                                # Логи работы
│
├── parser/                                # Парсер документации
│   ├── __init__.py
│   ├── link_parser.py                      # Сбор ссылок
│   ├── page_parser.py                       # Парсинг страниц
│   └── slicing_json.py                        # Нарезка JSON
│
├── telegram_bot/                            # Telegram бот
│   ├── __init__.py
│   └── bot.py                                 # Основной файл
│
└── yandex_gpt/                                # Yandex GPT
    ├── __init__.py
    ├── create_assistant.py                      # Создание ассистента
    ├── create_index.py                            # Создание индекса
    └── test_assistant.py                            # Тестирование
```

Быстрый старт
1. Установка
```
bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. .env файл
```
env
BOT_TOKEN=ваш_токен
DATABASE_URL=postgresql+asyncpg://postgres:123@localhost:5432/bitrix_bot
FOLDER_ID=ваш_id_папки_yandex_cloud
API_KEY=ваш_api_ключ_yandex_cloud
ASSISTANT_ID=id_ассистента
INDEX_ID=id_индекса

postgre.sql
DB_USER=postgres
DB_PASS=123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bitrix_bot
DATABASE_URL=postgresql+asyncpg://postgres:123@localhost:5432/bitrix_bot
```
3. База данных
```
bash
sudo -u postgres psql -c "CREATE DATABASE bitrix_bot OWNER postgres;"
alembic upgrade head
```

4. Запуск
```
bash
python3 telegram_bot/bot.py
```

requirements.txt
# Telegram бот
python-telegram-bot==21.0
# База данных
sqlalchemy==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
alembic==1.12.1
# Переменные окружения
python-dotenv==1.0.0
# Yandex Cloud SDK
yandex-ai-studio-sdk==0.19.2

# Автоматический запуск
schedule==1.2.0



# Модели БД (database/models.py)
class User(Base):
    telegram_id, username, first_name, thread_id

class Conversation(Base):
    user_id, question, answer, created_at

class Cache(Base):
    question_hash, question, answer, hits
Команды бота
/start — приветствие

/new — новый диалог (сброс контекста)

# Полезные команды

# Миграции
alembic revision --autogenerate -m "описание"
alembic upgrade head

# Проверка БД
sudo -u postgres psql -d bitrix_bot -c "SELECT * FROM users;"

# Создание индекса
python yandex_gpt/create_index.py