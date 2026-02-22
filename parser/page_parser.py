from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import json
import os

try:
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
except Exception as e:
    print(f"Ошибка запуска ChromeDriver: {e}")
    exit(1)


def parse_tables(driver):
    """Парсинг таблиц"""
    tables = driver.find_elements(By.TAG_NAME, "table")
    all_tables = []

    for table_id, table in enumerate(tables):
        table_data = []
        rows = table.find_elements(By.XPATH, ".//tr")
        
        for row in rows[1:]: 
            cells = row.find_elements(By.XPATH, ".//td | .//th")
            row_data = [cell.text.strip() for cell in cells]
            if row_data:
                table_data.append(row_data)

        if table_data:
            all_tables.append({
                "index": table_id,
                "data": table_data
            })
    return all_tables


def get_url(driver):
    """Получение URL """
    try:
        link_element = driver.find_element(By.TAG_NAME, "a")
        link_text = link_element.text.strip()
        href = link_element.get_attribute("href")
        return {
            "text": link_text,
            "url": href
        }
    except:
        return None


def get_title(driver):
    """Получение заголовка"""
    try:
        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
        return {
            "title": title
        }
    except:
        return {"title": ""}


def get_subtitles(driver):
    """Получение всех подзаголовков """
    try:
        subtitles = driver.find_elements(By.TAG_NAME, "h2")
        subs = []
        for subtitle in subtitles:
            sub = subtitle.text.strip()
            if sub:
                subs.append(sub)
        return {
            "subtitles": subs
        }
    except:
        return {"subtitles": []}


def get_text(driver):
    """Получение текста из параграфов с исключением служебных фраз"""
    skip_words = ["обновляем эту страницу", "может не хватать некоторых данных"]
    string = ""
    try:
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        for p in paragraphs:
            txt = p.text.strip()
            if txt:
                if not any(word in txt.lower() for word in skip_words):
                    string += " " + txt
        return string.strip()
    except:
        return ""


def get_code(driver):
    """Получение блоков кода"""
    try:
        codes = []
        code_blocks = driver.find_elements(By.XPATH, ".//code")
        for block in code_blocks:
            code_text = block.text.strip()
            if code_text and len(code_text) > 20:  
                codes.append(code_text)
        return {"code_examples": codes}
    except:
        return {"code_examples": []}


def get_lists(driver):
    """Получение полезных списков"""
    try:
        
        content = driver.find_elements(By.XPATH, "//main | //article | //div[@class='content'] | //div[@class='main-content']")
        
        if content:
            lists = content[0].find_elements(By.XPATH, ".//ul | .//ol")
        else:
            lists = driver.find_elements(By.XPATH, "//ul[not(ancestor::nav)] | //ol[not(ancestor::nav)]")
        
        useful_lists = []
        for lst in lists:
            items = [li.text.strip() for li in lst.find_elements(By.XPATH, ".//li") if li.text.strip()]
            if items and len(items) < 30 and not any("справочник" in item.lower() for item in items[:3]):
                useful_lists.append({
                    "type": lst.tag_name,
                    "items": items
                })
        
        return {"lists": useful_lists}
    except:
        return {"lists": []}



try:
    with open('all_links.json', 'r', encoding='utf-8') as f:
        links_list = json.load(f)
    print(f"Загружено {len(links_list)} ссылок")
except json.JSONDecodeError as e:
    print(f"Ошибка в JSON файле: {e}")
    driver.quit()
    exit(1)
except FileNotFoundError:
    print("Файл all_links.json не найден!")
    driver.quit()
    exit(1)

output_file = 'all_parsed_pages1.json'


if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        all_pages_data = json.load(f)
else:
    all_pages_data = {}
   



for link_item in links_list:
    page_name = link_item['text']
    page_url = link_item['url']
   
    
    if page_url in all_pages_data:
        continue
    
    
    try:
        driver.get(page_url)
        time.sleep(3)  
        
        page_data = {
            "name": page_name,
            "url": page_url,
            "title": get_title(driver)["title"],
            "subtitles": get_subtitles(driver)["subtitles"],
            "text": get_text(driver),
            "tables": parse_tables(driver),
            "code": get_code(driver)["code_examples"],
            "lists": get_lists(driver)["lists"]
        }
        
        all_pages_data[page_url] = page_data

        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_pages_data, f, ensure_ascii=False, indent=2)
        
        time.sleep(1)
        
    except Exception as e:
        print(f" Ошибка: {e}")

        all_pages_data[page_url] = {
            "url": page_url,
            "error": str(e),
            "title": "ОШИБКА ЗАГРУЗКИ"
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_pages_data, f, ensure_ascii=False, indent=2)


