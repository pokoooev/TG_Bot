import os
from yandex_cloud_ml_sdk import YCloudML

FOLDER_ID = os.getenv("FOLDER_ID")
API_KEY = os.getenv("API_KEY")

sdk = YCloudML(folder_id=FOLDER_ID, auth=API_KEY)

def create_thread():
    return sdk.threads.create(ttl_days=1, expiration_policy="static")

def create_assistant(model_uri=None, tools=None):
    """Создает ассистента
    
    Args:
        model_uri: строка с URI модели (например, "gpt://b1ge7nqks9hgsbtac2va/yandexgpt/latest")
        tools: список инструментов
    """
    if model_uri is None:
        model_uri = f"gpt://{FOLDER_ID}/yandexgpt/latest"
    
    kwargs = {}
    if tools and len(tools) > 0:
        kwargs = {"tools": tools}
    

    return sdk.assistants.create(
        model=model_uri,  
        ttl_days=1, 
        expiration_policy="since_last_active",
        **kwargs
    )

def get_assistant(assistant_id):
    """Получает существующего ассистента по ID"""
    return sdk.assistants.get(assistant_id)

def update_assistant(assistant_id, instruction=None, tools=None):
    """Обновляет инструкцию и инструменты ассистента"""
    assistant = get_assistant(assistant_id)
    
    update_kwargs = {}
    if instruction:
        update_kwargs["instruction"] = instruction
    if tools is not None:
        update_kwargs["tools"] = tools
    
    if update_kwargs:
        return assistant.update(**update_kwargs)
    return assistant