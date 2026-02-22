"""
Оркестратор для периодического запуска парсеров
Запускает: link_parser.py → page_parser.py → slicing_json.py
"""

import subprocess
import time
import logging
import os
import sys
from datetime import datetime
import schedule  

# Настройка логирования
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"parser_scheduler_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
PARSER_DIR = os.path.dirname(os.path.abspath(__file__))
LINK_PARSER = os.path.join(PARSER_DIR, "parser", "link_parser.py")
PAGE_PARSER = os.path.join(PARSER_DIR, "parser", "page_parser.py")
SLICING_JSON = os.path.join(PARSER_DIR, "parser", "slicing_json.py")
VENV_PYTHON = os.path.join(PARSER_DIR, "venv", "bin", "python") 


def run_script(script_path, script_name):
    """Запускает Python скрипт и логирует результат"""
    logger.info(f"Запуск {script_name}...")
    
    try:
        # Используем python из виртуального окружения если есть
        python_path = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
        
        result = subprocess.run(
            [python_path, script_path],
            capture_output=True,
            text=True,
            timeout=3600  
        )
        
        if result.returncode == 0:
            logger.info(f"{script_name} выполнен успешно")
            if result.stdout:
                logger.info(f"Вывод: {result.stdout[-500:]}") 
            return True
        else:
            logger.error(f"{script_name} завершился с ошибкой (код {result.returncode})")
            logger.error(f"Stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"{script_name} превысил время ожидания")
        return False
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске {script_name}: {e}")
        return False


def run_full_pipeline():
    """Запускает полный конвейер парсинга"""

    
    # Сбор ссылок
    if not run_script(LINK_PARSER, "link_parser.py"):
        logger.error("Конвейер остановлен на этапе link_parser")
        return False
    
    # Парсинг страниц
    if not run_script(PAGE_PARSER, "page_parser.py"):
        logger.error("Конвейер остановлен на этапе page_parser")
        return False
    
    # Нарезка JSON
    if not run_script(SLICING_JSON, "slicing_json.py"):
        logger.error("Конвейер остановлен на этапе slicing_json")
        return False
    
    
    logger.info(f"КОНВЕЙЕР ЗАВЕРШЕН")
    return True


def run_link_parser_only():
    """Запускает только сбор ссылок"""
    logger.info("Запуск только link_parser.py")
    return run_script(LINK_PARSER, "link_parser.py")


def run_page_parser_only():
    """Запускает только парсинг страниц"""
    logger.info("Запуск только page_parser.py")
    return run_script(PAGE_PARSER, "page_parser.py")


def run_slicing_only():
    """Запускает только нарезку JSON"""
    logger.info("Запуск только slicing_json.py")
    return run_script(SLICING_JSON, "slicing_json.py")


def check_files():
    """Проверяет наличие всех необходимых файлов"""
    required_files = [LINK_PARSER, PAGE_PARSER, SLICING_JSON]
    missing = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(os.path.basename(file_path))
    
    if missing:
        logger.error(f"Отсутствуют файлы: {', '.join(missing)}")
        return False
    
    logger.info("Все необходимые файлы найдены")
    return True


def main():
    """Основная функция с выбором режима"""
    
    # Проверяем наличие файлов
    if not check_files():
        sys.exit(1)
    
    # Если передан аргумент командной строки
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "full":
            run_full_pipeline()
        elif mode == "links":
            run_link_parser_only()
        elif mode == "pages":
            run_page_parser_only()
        elif mode == "slice":
            run_slicing_only()
        elif mode == "schedule":
            # Запуск по расписанию
            logger.info("Запуск в режиме планировщика")
            
            schedule.every().sunday.at("04:00").do(run_full_pipeline)
            
            
            
            logger.info("Планировщик запущен")
            
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)  
            except KeyboardInterrupt:
                logger.info("Планировщик остановлен пользователем")
        else:
            print(f"Неизвестный режим: {mode}")
            print("Доступные режимы: full, links, pages, slice, schedule")
            sys.exit(1)
    else:
    
        run_full_pipeline()


if __name__ == "__main__":
    main()