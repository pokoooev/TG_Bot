from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import json

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get("https://apidocs.bitrix24.ru/")
time.sleep(3)


ref_button = driver.find_element("xpath", "//button[.//span[text()='Справочник API']]")
ref_button.click()
time.sleep(3)

# Находим родительский элемент Справочника API
parent_li = ref_button.find_element(By.XPATH, "ancestor::li")

# Раскрываем все вложенные разделы 
def expand_all_sections(parent_element):
    buttons = parent_element.find_elements(By.XPATH, ".//button")
    for button in buttons:
        try:
            if button.text.strip() and button.text.strip() != "Справочник API":
                driver.execute_script("arguments[0].click();", button)
                time.sleep(0.5)
                # Рекурсивно раскрываем вложенные кнопки
                expand_all_sections(button)
        except:
            continue


expand_all_sections(parent_li)
time.sleep(2)

# Теперь собираем ВСЕ ссылки внутри родительского элемента
all_links_in_section = parent_li.find_elements(By.XPATH, ".//a")

# Собираем в словарь
unique_links = {}

for link in all_links_in_section:
    try:
        text = link.text.strip()
        href = link.get_attribute("href")
        
        if not text or not href or not href.startswith("http"):
            continue
            
        # Исключаем служебные фразы
        if any(skip in text for skip in ["Справочник API", "Инструменты и сценарии"]):
            continue
            
        # Сохраняем по уникальному URL
        unique_links[href] = {
            'text': text,
            'url': href
        }
                
    except Exception as e:
        print(f"Ошибка при обработке ссылки: {e}")
        continue

api_links = list(unique_links.values())


with open('all_links.json', 'w', encoding='utf-8') as f:
    json.dump(api_links, f, ensure_ascii=False, indent=2, sort_keys=True)


