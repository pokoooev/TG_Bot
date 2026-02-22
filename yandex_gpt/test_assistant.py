from unittest import result
from yandex_ai_studio_sdk import AIStudio
from yandex_cloud_ml_sdk import YCloudML
import os

from create_assistant import create_assistant, create_thread, get_assistant, update_assistant

FOLDER_ID = os.getenv("FOLDER_ID")
API_KEY = os.getenv("API_KEY")
ASSISTANT_ID = open('assistant_id.txt').read().strip()
INDEX_ID = open('search_index_id.txt').read().strip()
sdk = YCloudML(folder_id=FOLDER_ID, auth=API_KEY)

search_tool = sdk.tools.search_index(INDEX_ID)


model_uri = f"gpt://{FOLDER_ID}/yandexgpt/latest"
        

thread = create_thread()

assistant = create_assistant(model_uri=model_uri, tools=[search_tool])
update_assistant(assistant.id,
    instruction= "Отвечай на вопрос подробно, задавай уточняющие вопросы и сохраняй контекст беседы, запоминая о какой сущности речь"
)




thread.write("что такое вайб")
run = assistant.run(thread)
result = run.wait()
print(result.text)  

thread.write("Какие блоки и элементы можно добавить на него?")
run = assistant.run(thread)
result = run.wait()
print(result.text)  

for msg in list(thread)[::-1]:
    print(f"**{msg.author.role}:{msg.text}")

thread.delete
assistant.delete