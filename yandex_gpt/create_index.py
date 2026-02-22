from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.search_indexes import (
    StaticIndexChunkingStrategy,
    HybridSearchIndexType,
    ReciprocalRankFusionIndexCombinationStrategy
)
import os
import time

FOLDER_ID = os.getenv("FOLDER_ID")
API_KEY = os.getenv("API_KEY")

sdk = YCloudML(folder_id=FOLDER_ID, auth=API_KEY)

file_ids = []
files_dir = "knowledge_base"

for filename in os.listdir(files_dir):
    if filename.endswith('.txt'):
        file_path = os.path.join(files_dir, filename)
        print(f"  Загружаю: {filename}")
        
        file_info = sdk.files.upload(
            file_path,
            labels={"type": "api_doc", "filename": filename}
        )
        file_ids.append(file_info.id)
        print(f"ID: {file_info.id}")



op = sdk.search_indexes.create_deferred(
    file_ids,
    index_type=HybridSearchIndexType(
        chunking_strategy=StaticIndexChunkingStrategy(
            max_chunk_size_tokens=1000,
            chunk_overlap_tokens=100
        ),
        combination_strategy=ReciprocalRankFusionIndexCombinationStrategy()
    ),

)

search_index = op.wait()
with open('search_index_id.txt', 'w') as f:
    f.write(search_index.id)