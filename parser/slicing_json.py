import json
import os
import re

# Читаем ваш JSON
with open('all_parsed_pages1.json', 'r', encoding='utf-8') as f:
    docs = json.load(f)

# Создаем папку для файлов
os.makedirs('knowledge_base', exist_ok=True)

# Для каждого метода создаем файл
for method_name, method_data in docs.items():
    
    safe_name = re.sub(r'[^\w\s-]', '', method_name).strip().replace(' ', '_')
    filename = f"knowledge_base/{safe_name}.txt"
    
    code_examples = method_data.get('code', [])
    if isinstance(code_examples, dict):
        code_examples = code_examples.get('code_examples', [])
    
    content = f"""# {method_name}
URL: {method_data.get('url', '')}

## ОПИСАНИЕ
{method_data.get('text', '')}

## ПРИМЕРЫ КОДА
"""
    if code_examples:
        for code in code_examples:
            if code:  
                content += f"\n{code}\n---\n"
    else:
        content += "Нет примеров кода\n"
    
    content += "\n## ТАБЛИЦЫ\n"
    

    tables = method_data.get('tables', [])
    if tables:
        for table in tables:
            content += f"\nТаблица {table.get('index', 0)}:\n"
            for row in table.get('data', []):
                content += f"{' | '.join(str(cell) for cell in row)}\n"
    else:
        content += "Нет таблиц\n"
    
    
    lists_data = method_data.get('lists', {})
    lists = lists_data.get('lists', []) if isinstance(lists_data, dict) else []
    
    if lists:
        content += "\n## СПИСКИ\n"
        for lst in lists:
            content += f"\n{lst.get('type', 'ul')}:\n"
            for item in lst.get('items', []):
                content += f"  • {item}\n"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Создан файл: {filename}")

print(f"\n Всего создано файлов: {len(os.listdir('knowledge_base'))}")